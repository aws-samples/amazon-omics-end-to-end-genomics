version 1.0

## Copyright Broad Institute, 2021
##
## This WDL pipeline implements data pre-processing according to the GATK Best Practices.
##
## Requirements/expectations :
## - Pair-end sequencing data in unmapped BAM (uBAM) format
## - One or more read groups, one per uBAM file, all belonging to a single sample (SM)
## - Input uBAM files must additionally comply with the following requirements:
## - - filenames all have the same suffix (we use ".unmapped.bam")
## - - files must pass validation by ValidateSamFile
## - - reads are provided in query-sorted order
## - - all reads must have an RG tag
##
## Output :
## - A clean BAM file and its index, suitable for variant discovery analyses.
##
## Cromwell version support
## - Successfully tested on v59
##
## Runtime parameters are optimized for Broad's Google Cloud Platform implementation.
##
## LICENSING :
## This script is released under the WDL source code license (BSD-3) (see LICENSE in
## https://github.com/broadinstitute/wdl). Note however that the programs it calls may
## be subject to different licenses. Users are responsible for checking that they are
## authorized to run all programs before running this script. Please see the dockers
## for detailed licensing information pertaining to the included programs.

# WORKFLOW DEFINITION
workflow PreProcessingForVariantDiscovery_GATK4 {
  input {
    String sample_name

    File unmapped_bam
    String unmapped_bam_suffix
    File ref_fasta
    File ref_fasta_index
    File ref_dict
    File ref_alt
    File ref_ann
    File ref_bwt
    File ref_pac
    File ref_amb
    File ref_sa
    File dbSNP_vcf
    File dbSNP_vcf_index
    File known_indels_vcf
    File known_indels_vcf_index
    File Mills_1000G_indels_vcf
    File Mills_1000G_indels_vcf_index
    String gatk_docker
    String gotc_docker

  }

  String ref_name = "hg38"
  #File ref_fasta = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.fasta"

  #String ref_base_ext = basename(ref_fasta)
  #String ref_base = basename(ref_fasta,".fasta")
  #String ref_base_path = sub(ref_fasta,ref_base_ext,"")
  #String dbSNP_vcf_index_path = sub(dbSNP_vcf,".vcf",".vcf.idx")
  #String known_indels_vcf_path = sub(known_indels_vcf,".vcf.gz",".vcf.gz.tbi")
  #String Mills_1000G_indels_vcf_path = sub(Mills_1000G_indels_vcf,".vcf.gz",".vcf.gz.tbi")

  #File ref_fasta_index = ref_base_path + ref_base_ext + ".fai"
  #File ref_dict = ref_base_path + ref_base + ".dict"
  #File ref_alt = ref_base_path + ref_base_ext + ".64.alt"
  #File ref_sa = ref_base_path + ref_base_ext + ".64.sa"
  #File ref_ann = ref_base_path + ref_base_ext + ".64.ann"
  #File ref_bwt = ref_base_path + ref_base_ext + ".64.bwt"
  #File ref_pac = ref_base_path + ref_base_ext + ".64.pac"
 # File ref_amb = ref_base_path + ref_base_ext + ".64.amb"

  #File dbSNP_vcf_index = dbSNP_vcf_index_path
  #File known_indels_vcf_index = known_indels_vcf_path
  #File Mills_1000G_indels_vcf_index = Mills_1000G_indels_vcf_path

  #File ref_fasta_index = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.fai"
  #File ref_dict = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.dict"
  #File ref_alt = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.alt"
  #File ref_sa = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.sa"
  #File ref_ann = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.ann"
  #File ref_bwt = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.bwt"
  #File ref_pac = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.pac"
  #File ref_amb = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.amb"
  #File dbSNP_vcf = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.dbsnp138.vcf"
  #File dbSNP_vcf_index = "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.dbsnp138.vcf.idx"
  #Array[File] known_indels_sites_VCFs = [
  #                                      "s3://broad-references/hg38/v0/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz",
  #                                      "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.known_indels.vcf.gz"
  #                                      ]
  #Array[File] known_indels_sites_indices = [
  #                                         "s3://broad-references/hg38/v0/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz.tbi",
  #                                         "s3://broad-references/hg38/v0/Homo_sapiens_assembly38.known_indels.vcf.gz.tbi"
  #                                         ]


  String bwa_commandline = "bwa mem -K 100000000 -p -v 3 -t 14 -Y $bash_ref_fasta"
  Int compression_level = 6

  #String gatk_docker = "022521056385.dkr.ecr.us-east-1.amazonaws.com/gatk:4.1.9.0"
  String gatk_path = "/gatk/gatk"
  #String gotc_docker = "022521056385.dkr.ecr.us-east-1.amazonaws.com/genomes-in-the-cloud:2.4.7-1603303710"
  String gotc_path = "/usr/gitc/"
  # Amazon linux has python installed

  String base_file_name = sample_name + "." + ref_name

  #Array[File] flowcell_unmapped_bams = read_lines(flowcell_unmapped_bams_list)

  #File unmapped_bam = unmapped_bam

  # Get the version of BWA to include in the PG record in the header of the BAM produced
  # by MergeBamAlignment.
  call GetBwaVersion {
    input:
      docker_image = gotc_docker,
      bwa_path = gotc_path,
  }

  # Align flowcell-level unmapped input bams in parallel

    # Get the basename, i.e. strip the filepath and the extension
    String bam_basename = basename(unmapped_bam, unmapped_bam_suffix)

    # Map reads to reference
    call SamToFastqAndBwaMem {
      input:
        input_bam = unmapped_bam,
        bwa_commandline = bwa_commandline,
        output_bam_basename = bam_basename + ".unmerged",
        ref_fasta = ref_fasta,
        ref_fasta_index = ref_fasta_index,
        ref_dict = ref_dict,
        ref_alt = ref_alt,
        ref_sa = ref_sa,
        ref_ann = ref_ann,
        ref_bwt = ref_bwt,
        ref_pac = ref_pac,
        ref_amb = ref_amb,
        docker_image = gotc_docker,
        bwa_path = gotc_path,
        gotc_path = gotc_path,
        compression_level = compression_level
    }

    # Merge original uBAM and BWA-aligned BAM
    call MergeBamAlignment {
      input:
        unmapped_bam = unmapped_bam,
        bwa_commandline = bwa_commandline,
        bwa_version = GetBwaVersion.version,
        aligned_bam = SamToFastqAndBwaMem.output_bam,
        output_bam_basename = bam_basename + ".aligned.unsorted",
        ref_fasta = ref_fasta,
        ref_fasta_index = ref_fasta_index,
        ref_dict = ref_dict,
        docker_image = gatk_docker,
        gatk_path = gatk_path,
        compression_level = compression_level
    }

  # Aggregate aligned+merged flowcell BAM files and mark duplicates
  # We take advantage of the tool's ability to take multiple BAM inputs and write out a single output
  # to avoid having to spend time just merging BAM files.
  call MarkDuplicates {
    input:
      input_bams = MergeBamAlignment.output_bam,
      output_bam_basename = base_file_name + ".aligned.unsorted.duplicates_marked",
      metrics_filename = base_file_name + ".duplicate_metrics",
      docker_image = gatk_docker,
      gatk_path = gatk_path,
      compression_level = compression_level,
  }

  # Sort aggregated+deduped BAM file and fix tags
  call SortAndFixTags {
    input:
      input_bam = MarkDuplicates.output_bam,
      output_bam_basename = base_file_name + ".aligned.duplicate_marked.sorted",
      ref_dict = ref_dict,
      ref_fasta = ref_fasta,
      ref_fasta_index = ref_fasta_index,
      docker_image = gatk_docker,
      gatk_path = gatk_path,
      compression_level = compression_level
  }

  # Create list of sequences for scatter-gather parallelization
  call CreateSequenceGroupingTSV {
    input:
      ref_dict = ref_dict,
      docker_image = gotc_docker,
  }

  # Perform Base Quality Score Recalibration (BQSR) on the sorted BAM in parallel
  scatter (subgroup in CreateSequenceGroupingTSV.sequence_grouping) {
    # Generate the recalibration model by interval
    call BaseRecalibrator {
      input:
        input_bam = SortAndFixTags.output_bam,
        input_bam_index = SortAndFixTags.output_bam_index,
        recalibration_report_filename = base_file_name + ".recal_data.csv",
        sequence_group_interval = subgroup,
        dbSNP_vcf = dbSNP_vcf,
        dbSNP_vcf_index = dbSNP_vcf_index,
        known_indels_vcf = known_indels_vcf,
        known_indels_vcf_index = known_indels_vcf_index,
        Mills_1000G_indels_vcf = Mills_1000G_indels_vcf,
        Mills_1000G_indels_vcf_index = Mills_1000G_indels_vcf_index,
        ref_dict = ref_dict,
        ref_fasta = ref_fasta,
        ref_fasta_index = ref_fasta_index,
        docker_image = gatk_docker,
        gatk_path = gatk_path,
    }
  }

  # Merge the recalibration reports resulting from by-interval recalibration
  call GatherBqsrReports {
    input:
      input_bqsr_reports = BaseRecalibrator.recalibration_report,
      output_report_filename = base_file_name + ".recal_data.csv",
      docker_image = gatk_docker,
      gatk_path = gatk_path,
  }

  scatter (subgroup in CreateSequenceGroupingTSV.sequence_grouping_with_unmapped) {

    # Apply the recalibration model by interval
    call ApplyBQSR {
      input:
        input_bam = SortAndFixTags.output_bam,
        input_bam_index = SortAndFixTags.output_bam_index,
        output_bam_basename = base_file_name + ".aligned.duplicates_marked.recalibrated",
        recalibration_report = GatherBqsrReports.output_bqsr_report,
        sequence_group_interval = subgroup,
        ref_dict = ref_dict,
        ref_fasta = ref_fasta,
        ref_fasta_index = ref_fasta_index,
        docker_image = gatk_docker,
        gatk_path = gatk_path,
    }
  }

  # Merge the recalibrated BAM files resulting from by-interval recalibration
  call GatherBamFiles {
    input:
      input_bams = ApplyBQSR.recalibrated_bam,
      output_bam_basename = base_file_name,
      docker_image = gatk_docker,
      gatk_path = gatk_path,
      compression_level = compression_level
  }

  # Outputs that will be retained when execution is complete
  output {
    File duplication_metrics = MarkDuplicates.duplicate_metrics
    File bqsr_report = GatherBqsrReports.output_bqsr_report
    File analysis_ready_bam = GatherBamFiles.output_bam
    File analysis_ready_bam_index = GatherBamFiles.output_bam_index
    File analysis_ready_bam_md5 = GatherBamFiles.output_bam_md5
  }
}

# TASK DEFINITIONS

# Get version of BWA
task GetBwaVersion {
  input {
    Float mem_size_gb = 1
    String docker_image
    String bwa_path
  }

  command {
    echo GetBwaVersion >&2

    # Not setting "set -o pipefail" here because /bwa has a rc=1 and we don't want to allow rc=1 to succeed
    # because the sed may also fail with that error and that is something we actually want to fail on.

    set -ux

    ~{bwa_path}bwa 2>&1 | \
    grep -e '^Version' | \
    sed 's/Version: //'
  }
  runtime {
    docker: docker_image
    memory: "~{mem_size_gb} GiB"
  }
  output {
    String version = read_string(stdout())
  }
}

# Read unmapped BAM, convert on-the-fly to FASTQ and stream to BWA MEM for alignment
task SamToFastqAndBwaMem {
  # This is the .alt file from bwa-kit (https://github.com/lh3/bwa/tree/master/bwakit),
  # listing the reference contigs that are "alternative". Leave blank in JSON for legacy
  # references such as b37 and hg19.
  input {
    File input_bam
    String bwa_commandline
    String output_bam_basename
    File ref_fasta
    File ref_fasta_index
    File ref_dict
    File? ref_alt
    File ref_amb
    File ref_ann
    File ref_bwt
    File ref_pac
    File ref_sa

    Float mem_size_gb = 56
    Int num_cpu = 32

    Int compression_level

    String docker_image
    String bwa_path
    String gotc_path
  }

  command {
    set -euo pipefail

    # set the bash variable needed for the command-line
    bash_ref_fasta=~{ref_fasta}

    java -Xmx8G -jar ~{gotc_path}picard.jar \
    SamToFastq \
    INPUT=~{input_bam} \
    FASTQ=/dev/stdout \
    INTERLEAVE=true \
    NON_PF=true \
    | \
    ~{bwa_path}~{bwa_commandline} /dev/stdin - \
    | \
    samtools view -1 - > ~{output_bam_basename}.bam
  }
  runtime {
    docker: docker_image
    memory: "~{mem_size_gb} GiB"
    cpu: num_cpu
  }
  output {
    File output_bam = "~{output_bam_basename}.bam"
  }
}

# Merge original input uBAM file with BWA-aligned BAM file
task MergeBamAlignment {
  input {
    File unmapped_bam
    String bwa_commandline
    String bwa_version
    File aligned_bam
    String output_bam_basename
    File ref_fasta
    File ref_fasta_index
    File ref_dict

    Int compression_level
    Int mem_size_gb = 32

    String docker_image
    String gatk_path
  }

  Int command_mem_gb = ceil(mem_size_gb) - 1

  command {
    echo MergeBamAlignment >&2

    set -euxo pipefail

    # set the bash variable needed for the command-line
    bash_ref_fasta=~{ref_fasta}
    ~{gatk_path} --java-options "-Dsamjdk.compression_level=~{compression_level} -Xmx~{command_mem_gb}G"  \
    MergeBamAlignment \
    --VALIDATION_STRINGENCY SILENT \
    --EXPECTED_ORIENTATIONS FR \
    --ATTRIBUTES_TO_RETAIN X0 \
    --ALIGNED_BAM ~{aligned_bam} \
    --UNMAPPED_BAM ~{unmapped_bam} \
    --OUTPUT ~{output_bam_basename}.bam \
    --REFERENCE_SEQUENCE ~{ref_fasta} \
    --PAIRED_RUN true \
    --SORT_ORDER "unsorted" \
    --IS_BISULFITE_SEQUENCE false \
    --ALIGNED_READS_ONLY false \
    --CLIP_ADAPTERS false \
    --ADD_MATE_CIGAR true \
    --MAX_INSERTIONS_OR_DELETIONS -1 \
    --PRIMARY_ALIGNMENT_STRATEGY MostDistant \
    --PROGRAM_RECORD_ID "bwamem" \
    --PROGRAM_GROUP_VERSION "~{bwa_version}" \
    --PROGRAM_GROUP_COMMAND_LINE "~{bwa_commandline}" \
    --PROGRAM_GROUP_NAME "bwamem" \
    --UNMAPPED_READ_STRATEGY COPY_TO_TAG \
    --ALIGNER_PROPER_PAIR_FLAGS true \
    --UNMAP_CONTAMINANT_READS true
  }
  runtime {
    docker: docker_image
    memory: "~{mem_size_gb} GiB"
    cpu: 2
  }
  output {
    File output_bam = "~{output_bam_basename}.bam"
  }
}

# Sort BAM file by coordinate order and fix tag values for NM and UQ
task SortAndFixTags {
  input {
    File input_bam
    String output_bam_basename
    File ref_dict
    File ref_fasta
    File ref_fasta_index

    Int compression_level
    Float mem_size_gb = 512

    String docker_image
    String gatk_path
  }

  command {
    echo SortAndFixTags >&2

    set -euxo pipefail

    ~{gatk_path} --java-options "-Xmx480G -Xms480G" \
    SortSam \
    --INPUT ~{input_bam} \
    --OUTPUT /dev/stdout \
    --SORT_ORDER "coordinate" \
    --CREATE_INDEX false \
    --CREATE_MD5_FILE false \
    | \
    ~{gatk_path} --java-options "-Dsamjdk.compression_level=6 -Xmx18G -Xms18G" \
    SetNmMdAndUqTags \
    --INPUT /dev/stdin \
    --OUTPUT ~{output_bam_basename}.bam \
    --CREATE_INDEX true \
    --CREATE_MD5_FILE false \
    --REFERENCE_SEQUENCE ~{ref_fasta}

  }
  runtime {
    docker: docker_image
    memory: "~{mem_size_gb} GiB"
    cpu: 8
  }
  output {
    File output_bam = "~{output_bam_basename}.bam"
    File output_bam_index = "~{output_bam_basename}.bai"
  }
}

# Mark duplicate reads to avoid counting non-independent observations
task MarkDuplicates {
  input {
    File input_bams
    String output_bam_basename
    String metrics_filename

    Int compression_level
    Float mem_size_gb = 512

    String docker_image
    String gatk_path
  }

  Int xmx = ceil(mem_size_gb) - 8
  # Task is assuming query-sorted input so that the Secondary and Supplementary reads get marked correctly.
  # This works because the output of BWA is query-grouped and therefore, so is the output of MergeBamAlignment.
  # While query-grouped isn't actually query-sorted, it's good enough for MarkDuplicates with ASSUME_SORT_ORDER="queryname"
  command {
    echo MarkDuplicates >&2

    set -euxo pipefail

    ~{gatk_path} --java-options "-Dsamjdk.compression_level=~{compression_level} -Xms~{xmx}G -Xmx~{xmx}G" \
    MarkDuplicates \
    --INPUT  ~{input_bams} \
    --OUTPUT ~{output_bam_basename}.bam \
    --METRICS_FILE ~{metrics_filename} \
    --VALIDATION_STRINGENCY SILENT \
    --OPTICAL_DUPLICATE_PIXEL_DISTANCE 2500 \
    --ASSUME_SORT_ORDER "queryname" \
    --CREATE_MD5_FILE false
  }
  runtime {
    docker: docker_image
    memory: "~{mem_size_gb}  GiB"
    cpu: 4
  }
  output {
    File output_bam = "~{output_bam_basename}.bam"
    File duplicate_metrics = "~{metrics_filename}"
  }
}

# Generate sets of intervals for scatter-gathering over chromosomes
task CreateSequenceGroupingTSV {
  input {
    File ref_dict
    Float mem_size_gb = 2
    String docker_image
  }
  # Use python to create the Sequencing Groupings used for BQSR and PrintReads Scatter.
  # It outputs to stdout where it is parsed into a wdl Array[Array[String]]
  # e.g. [["1"], ["2"], ["3", "4"], ["5"], ["6", "7", "8"]]
  command <<<

    echo CreateSequenceGroupingTSV >&2

    python <<CODE
    with open("~{ref_dict}", "r") as ref_dict_file:
        sequence_tuple_list = []
        longest_sequence = 0
        for line in ref_dict_file:
            if line.startswith("@SQ"):
                line_split = line.split("\t")
                # (Sequence_Name, Sequence_Length)
                sequence_tuple_list.append((line_split[1].split("SN:")[1], int(line_split[2].split("LN:")[1])))
        longest_sequence = sorted(sequence_tuple_list, key=lambda x: x[1], reverse=True)[0][1]
    # We are adding this to the intervals because hg38 has contigs named with embedded colons (:) and a bug in
    # some versions of GATK strips off the last element after a colon, so we add this as a sacrificial element.
    hg38_protection_tag = ":1+"
    # initialize the tsv string with the first sequence
    tsv_string = sequence_tuple_list[0][0] + hg38_protection_tag
    temp_size = sequence_tuple_list[0][1]
    for sequence_tuple in sequence_tuple_list[1:]:
        if temp_size + sequence_tuple[1] <= longest_sequence:
            temp_size += sequence_tuple[1]
            tsv_string += "\t" + sequence_tuple[0] + hg38_protection_tag
        else:
            tsv_string += "\n" + sequence_tuple[0] + hg38_protection_tag
            temp_size = sequence_tuple[1]
    # add the unmapped sequences as a separate line to ensure that they are recalibrated as well
    with open("sequence_grouping.txt","w") as tsv_file:
      tsv_file.write(tsv_string)
      tsv_file.close()

    tsv_string += '\n' + "unmapped"

    with open("sequence_grouping_with_unmapped.txt","w") as tsv_file_with_unmapped:
      tsv_file_with_unmapped.write(tsv_string)
      tsv_file_with_unmapped.close()
    CODE

    cat sequence_grouping_with_unmapped.txt
  >>>
  runtime {
    docker: docker_image
    memory: "~{mem_size_gb} GiB"
    cpu: 2
  }
  output {
    Array[Array[String]] sequence_grouping = read_tsv("sequence_grouping.txt")
    Array[Array[String]] sequence_grouping_with_unmapped = read_tsv("sequence_grouping_with_unmapped.txt")
  }
}

# Generate Base Quality Score Recalibration (BQSR) model
task BaseRecalibrator {
  input {
    File input_bam
    File input_bam_index
    String recalibration_report_filename
    Array[String] sequence_group_interval
    File dbSNP_vcf
    File dbSNP_vcf_index
    File known_indels_vcf
    File known_indels_vcf_index
    File Mills_1000G_indels_vcf
    File Mills_1000G_indels_vcf_index
    #Array[File] known_indels_sites_indices
    File ref_dict
    File ref_fasta
    File ref_fasta_index

    Float mem_size_gb = 30

    String docker_image
    String gatk_path
  }

  Int xmx = ceil(mem_size_gb) - 2

  command {
    echo BaseRecalibrator >&2
    set -euxo pipefail

    ~{gatk_path} --java-options "-Xmx~{xmx}G" \
    BaseRecalibrator \
    -R ~{ref_fasta} \
    -I ~{input_bam} \
    --use-original-qualities \
    -O ~{recalibration_report_filename} \
    --known-sites ~{dbSNP_vcf} \
    --known-sites ~{known_indels_vcf} \
    --known-sites ~{Mills_1000G_indels_vcf} \
    -L ~{sep=" -L " sequence_group_interval}
  }
  runtime {
    docker: docker_image
    memory: "~{mem_size_gb} GiB"
    cpu: 2
  }
  output {
    File recalibration_report = "~{recalibration_report_filename}"
  }
}

# Combine multiple recalibration tables from scattered BaseRecalibrator runs
task GatherBqsrReports {
  input {
    Array[File] input_bqsr_reports
    String output_report_filename

    Float mem_size_gb = 8

    String docker_image
    String gatk_path
  }

  Int xmx = ceil(mem_size_gb) - 2

  command {
    echo GatherBqsrReports
    set -euxo pipefail

    ~{gatk_path} --java-options "-Xmx~{xmx}G" \
    GatherBQSRReports \
    -I ~{sep=' -I ' input_bqsr_reports} \
    -O ~{output_report_filename}
  }
  runtime {
    docker: docker_image
    memory: "~{mem_size_gb} GiB"
    cpu: 2
  }
  output {
    File output_bqsr_report = "~{output_report_filename}"
  }
}

# Apply Base Quality Score Recalibration (BQSR) model
task ApplyBQSR {
  input {
    File input_bam
    File input_bam_index
    String output_bam_basename
    File recalibration_report
    Array[String] sequence_group_interval
    File ref_dict
    File ref_fasta
    File ref_fasta_index

    Float mem_size_gb = 8

    String docker_image
    String gatk_path
  }

  Int xmx = ceil(mem_size_gb) - 2
  command {
    echo ApplyBQSR
    set -euxo pipefail

    ~{gatk_path} --java-options "-Dsamjdk.compression_level=6 -Xmx~{xmx}G" \
    ApplyBQSR \
    -R ~{ref_fasta} \
    -I ~{input_bam} \
    -O ~{output_bam_basename}.bam \
    -L ~{sep=" -L " sequence_group_interval} \
    -bqsr ~{recalibration_report} \
    --static-quantized-quals 10 --static-quantized-quals 20 --static-quantized-quals 30 \
    --add-output-sam-program-record \
    --create-output-bam-md5 \
    --use-original-qualities
  }
  runtime {
    docker: docker_image
    memory: "~{mem_size_gb} GiB"
    cpu: 2
  }
  output {
    File recalibrated_bam = "~{output_bam_basename}.bam"
  }
}

# Combine multiple recalibrated BAM files from scattered ApplyRecalibration runs
task GatherBamFiles {
  input {
    Array[File] input_bams
    String output_bam_basename

    Int compression_level
    Float mem_size_gb = 4

    String docker_image
    String gatk_path
  }

  Int xmx = ceil(mem_size_gb) - 2

  command {
    echo GatherBamFiles
    set -euxo pipefail

    ~{gatk_path} --java-options "-Dsamjdk.compression_level=~{compression_level} -Xmx~{xmx}G" \
    GatherBamFiles \
    --INPUT ~{sep=' --INPUT ' input_bams} \
    --OUTPUT ~{output_bam_basename}.bam \
    --CREATE_INDEX true \
    --CREATE_MD5_FILE true
  }
  runtime {
    docker: docker_image
    memory: "~{mem_size_gb} GiB"
    cpu: 2
  }
  output {
    File output_bam = "~{output_bam_basename}.bam"
    File output_bam_index = "~{output_bam_basename}.bai"
    File output_bam_md5 = "~{output_bam_basename}.bam.md5"
  }
}
