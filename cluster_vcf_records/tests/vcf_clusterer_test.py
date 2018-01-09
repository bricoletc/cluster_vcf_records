import filecmp
import os
import unittest

from cluster_vcf_records import vcf_clusterer, vcf_record, vcf_record_cluster

modules_dir = os.path.dirname(os.path.abspath(vcf_clusterer.__file__))
data_dir = os.path.join(modules_dir, 'tests', 'data', 'vcf_clusterer')


class TestVcfClusterer(unittest.TestCase):
    def test_load_vcf_files(self):
        '''test _load_vcf_files'''
        vcf_file_1 = os.path.join(data_dir, 'load_vcf_files.1.vcf')

        expected_headers = {
            vcf_file_1: ['#file1 header1', '#file1 header2'],
        }

        expected_records = {
            'ref.1': [
                vcf_record.VcfRecord('ref.1\t5\tid3\tG\tA\tPASS\tSVTYPE=SNP\tGT\t1/1'),
                vcf_record.VcfRecord('ref.1\t10\tid1\tA\tT\tPASS\tSVTYPE=SNP\tGT\t1/1'),
            ],
            'ref.2': [vcf_record.VcfRecord('ref.2\t42\tid2\tG\tC\tPASS\tSVTYPE=SNP\tGT\t1/1')],
        }

        expected_sample = 'sample'
        got_sample, got_headers, got_records = vcf_clusterer.VcfClusterer._load_vcf_files([vcf_file_1])
        self.assertEqual(expected_sample, got_sample)
        self.assertEqual(expected_headers, got_headers)
        self.assertEqual(expected_records, got_records)

        vcf_file_2 = os.path.join(data_dir, 'load_vcf_files.2.vcf')
        expected_headers[vcf_file_2] = ['#file2 header', '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tsample_from_vcf_2']
        expected_records['ref.3'] = [vcf_record.VcfRecord('ref.3\t8\tid5\tA\tG\tPASS\tSVTYPE=SNP\tGT\t1/1')]
        expected_records['ref.1'].insert(1, vcf_record.VcfRecord('ref.1\t8\tid4\tC\tG\tPASS\tSVTYPE=SNP\tGT\t1/1'))
        expected_sample = 'sample_from_vcf_2'
        got_sample, got_headers, got_records = vcf_clusterer.VcfClusterer._load_vcf_files([vcf_file_1, vcf_file_2])
        self.assertEqual(expected_sample, got_sample)
        self.assertEqual(expected_headers, got_headers)
        self.assertEqual(expected_records, got_records)


    def test_cluster_vcf_record_list(self):
        '''test _cluster_vcf_record_list'''
        record1 = vcf_record.VcfRecord('ref_42\t11\tid_1\tA\tG\t42.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,52:39.80')
        record2 = vcf_record.VcfRecord('ref_42\t12\tid_2\tC\tG\t42.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,52:39.80')
        record3 = vcf_record.VcfRecord('ref_42\t15\tid_2\tC\tG\t42.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,52:39.80')
        record4 = vcf_record.VcfRecord('ref_42\t19\tid_2\tCCCCC\tG\t42.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,52:39.80')
        record5 = vcf_record.VcfRecord('ref_42\t23\tid_2\tC\tG\t42.42\tPASS\tKMER=31;SVLEN=0;SVTYPE=SNP\tGT:COV:GT_CONF\t1/1:0,52:39.80')
        record_list = [record1, record2, record3, record4, record5]
        cluster1 = vcf_record_cluster.VcfRecordCluster(vcf_record=record1, max_distance_between_variants=3)
        self.assertTrue(cluster1.add_vcf_record(record2))
        self.assertTrue(cluster1.add_vcf_record(record3))
        cluster2 = vcf_record_cluster.VcfRecordCluster(vcf_record=record4, max_distance_between_variants=3)
        self.assertTrue(cluster2.add_vcf_record(record5))
        expected = [cluster1, cluster2]
        got = vcf_clusterer.VcfClusterer._cluster_vcf_record_list(record_list, max_distance_between_variants=3)
        self.assertEqual(expected, got)

        cluster1.max_distance_between_variants=5
        self.assertTrue(cluster1.add_vcf_record(record4))
        self.assertTrue(cluster1.add_vcf_record(record5))
        got = vcf_clusterer.VcfClusterer._cluster_vcf_record_list(record_list, max_distance_between_variants=5)
        self.assertEqual([cluster1], got)


    def test_run(self):
        '''test run'''
        vcf_files = [
            os.path.join(data_dir, 'run.1.vcf'),
            os.path.join(data_dir, 'run.2.vcf'),
        ]
        ref_fasta = os.path.join(data_dir, 'run.ref.fa')
        tmp_out = 'tmp.vcf_clusterer.run.out.vcf'
        clusterer = vcf_clusterer.VcfClusterer(vcf_files, ref_fasta, tmp_out, source='source_name')
        clusterer.run()
        expected_vcf = os.path.join(data_dir, 'run.out.vcf')
        self.assertTrue(filecmp.cmp(expected_vcf, tmp_out, shallow=False))
        os.unlink(tmp_out)
