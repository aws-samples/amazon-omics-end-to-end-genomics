version 1.0

import "sub-workflows/processing-for-variant-discovery-gatk4.wdl" as preprocess
import "sub-workflows/haplotypecaller-gvcf-gatk4.wdl" as haplotype
import "sub-workflows/fastq-to-bam.wdl" as fastq2bam

workflow fastqToVCF {
    input {
      String sample_name
      File fastq_1
      File fastq_2
      String readgroup_name
      String run_date
      String library_name
      String platform_name
      String sequencing_center
      File ref_fasta
      File dbSNP_vcf
      File known_indels_vcf

      File Mills_1000G_indels_vcf
 
      File scattered_calling_intervals_archive
      String gatk_docker
      String gotc_docker
      
    }
    String unmapped_bam_suffix="unmapped.bam"
 String ref_base_ext = basename(ref_fasta)
   String ref_base = basename(ref_fasta,".fasta")
   String ref_base_path = sub(ref_fasta,ref_base_ext,"")
   String dbSNP_vcf_index_path = sub(dbSNP_vcf,".vcf",".vcf.idx")
   String known_indels_vcf_path = sub(known_indels_vcf,".vcf.gz",".vcf.gz.tbi")
   String Mills_1000G_indels_vcf_path = sub(Mills_1000G_indels_vcf,".vcf.gz",".vcf.gz.tbi")

   File ref_fasta_index = ref_base_path + ref_base_ext + ".fai"
   File ref_dict = ref_base_path + ref_base + ".dict"
   File ref_alt = ref_base_path + ref_base_ext + ".64.alt"
   File ref_sa = ref_base_path + ref_base_ext + ".64.sa"
   File ref_ann = ref_base_path + ref_base_ext + ".64.ann"
   File ref_bwt = ref_base_path + ref_base_ext + ".64.bwt"
   File ref_pac = ref_base_path + ref_base_ext + ".64.pac"
   File ref_amb = ref_base_path + ref_base_ext + ".64.amb"

   File dbSNP_vcf_index = dbSNP_vcf_index_path
   File known_indels_vcf_index = known_indels_vcf_path
   File Mills_1000G_indels_vcf_index = Mills_1000G_indels_vcf_path

    call fastq2bam.ConvertPairedFastQsToUnmappedBamWf as Fastq2Bam {
      input:
        sample_name=sample_name,
        fastq_1=fastq_1, fastq_2=fastq_2,
        readgroup_name=readgroup_name,
        run_date = run_date,
        library_name = library_name,
        platform_name = platform_name,
        sequencing_center = sequencing_center,
	gatk_docker = gatk_docker
    }
    call preprocess.PreProcessingForVariantDiscovery_GATK4 as PreProcess {
        input:
          sample_name = sample_name,
          unmapped_bam = Fastq2Bam.output_unmapped_bam,
          unmapped_bam_suffix = unmapped_bam_suffix,
          ref_fasta = ref_fasta,
          ref_fasta_index = ref_fasta_index,
          ref_dict = ref_dict,
          ref_alt = ref_alt,
          ref_sa = ref_sa,
          ref_ann = ref_ann,
          ref_bwt = ref_bwt,
          ref_pac = ref_pac,
          ref_amb = ref_amb,
          dbSNP_vcf =  dbSNP_vcf,
          dbSNP_vcf_index =  dbSNP_vcf_index,
          known_indels_vcf = known_indels_vcf,
          known_indels_vcf_index = known_indels_vcf_index,
          Mills_1000G_indels_vcf = Mills_1000G_indels_vcf,
          Mills_1000G_indels_vcf_index = Mills_1000G_indels_vcf_index,
          gatk_docker = gatk_docker,
          gotc_docker = gotc_docker,
    }
    call haplotype.HaplotypeCallerGvcf_GATK4 as CallHaplotypes {
        input:
          input_bam = PreProcess.analysis_ready_bam,
          input_bam_index = PreProcess.analysis_ready_bam_index,
          ref_fasta = ref_fasta,
          ref_fasta_index = ref_fasta_index,
          ref_dict = ref_dict,
          scattered_calling_intervals_archive = scattered_calling_intervals_archive,
	  gatk_docker = gatk_docker,
	  gotc_docker = gotc_docker,

    }
    output {
        File duplication_metrics = PreProcess.duplication_metrics
        File bqsr_report = PreProcess.bqsr_report
        File analysis_ready_bam = PreProcess.analysis_ready_bam
        File analysis_ready_bam_index = PreProcess.analysis_ready_bam_index
        File analysis_ready_bam_md5 = PreProcess.analysis_ready_bam_md5
        File output_vcf = CallHaplotypes.output_vcf
        File output_vcf_index = CallHaplotypes.output_vcf_index
    }
}
