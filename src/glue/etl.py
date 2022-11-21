import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsglue.dynamicframe import DynamicFrame

# Script generated for node Custom Transform
def MyTransform(glueContext, dfc) -> DynamicFrameCollection:
    from pyspark.sql.functions import coalesce
    from awsglue.dynamicframe import DynamicFrame

    df0 = dfc.select(list(dfc.keys())[0]).toDF()

    df0.withColumn("patient_id", coalesce(df0.dg_patient_id, df0.patient_id))

    df0.withColumn("patient_id", coalesce(df0.rx_patient_id, df0.patient_id))

    df0.withColumn("patient_id", coalesce(df0.pr_patient_id, df0.patient_id))

    dyf = DynamicFrame.fromDF(df0, glueContext, "results")
    return DynamicFrameCollection({"CustomTransform0": dyf}, glueContext)


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node Novation_Rx
Novation_Rx_node1665891226598 = glueContext.create_dynamic_frame.from_catalog(
    database="phenotypicdb",
    table_name="ovation_rx_csv",
    transformation_ctx="Novation_Rx_node1665891226598",
)

# Script generated for node DiagnosisDF
DiagnosisDF_node1665691724279 = glueContext.create_dynamic_frame.from_catalog(
    database="phenotypicdb",
    table_name="ovation_diagnosis_csv",
    transformation_ctx="DiagnosisDF_node1665691724279",
)

# Script generated for node ClinicoGenomicsDF
ClinicoGenomicsDF_node1665689379027 = glueContext.create_dynamic_frame.from_catalog(
    database="phenotypicdb",
    table_name="ovation_clinicogenomics_csv",
    transformation_ctx="ClinicoGenomicsDF_node1665689379027",
)

# Script generated for node ProceduresDF
ProceduresDF_node1665690724543 = glueContext.create_dynamic_frame.from_catalog(
    database="phenotypicdb",
    table_name="ovation_procedures_csv",
    transformation_ctx="ProceduresDF_node1665690724543",
)

# Script generated for node Renamed keys for finalJoin
RenamedkeysforfinalJoin_node1665892999370 = ApplyMapping.apply(
    frame=Novation_Rx_node1665891226598,
    mappings=[
        ("patient_id", "string", "rx_patient_id", "string"),
        ("claim_id", "string", "rx_claim_id", "string"),
        ("ndc_product", "long", "ndc_product", "long"),
        ("quantity", "double", "quantity", "double"),
        ("uom", "string", "uom", "string"),
        ("prescriber_npi", "long", "prescriber_npi", "long"),
        ("brand_name", "string", "brand_name", "string"),
        ("generic_name", "string", "generic_name", "string"),
        ("dosage_form", "string", "dosage_form", "string"),
    ],
    transformation_ctx="RenamedkeysforfinalJoin_node1665892999370",
)

# Script generated for node Renamed keys for Join
RenamedkeysforJoin_node1665694312611 = ApplyMapping.apply(
    frame=DiagnosisDF_node1665691724279,
    mappings=[
        ("patient_id", "string", "dg_patient_id", "string"),
        ("claim_id", "string", "dg_claim_id", "string"),
        ("diagnosis_date", "string", "diagnosis_date", "string"),
        ("diagnosis_vocab", "string", "diagnosis_vocab", "string"),
        ("diagnosis_code", "string", "diagnosis_code", "string"),
        ("diagnosis_desc", "string", "diagnosis_desc", "string"),
        ("vocabulary_name", "string", "vocabulary_name", "string"),
    ],
    transformation_ctx="RenamedkeysforJoin_node1665694312611",
)

# Script generated for node ApplyFilteronClinicalGenomicsData
ApplyFilteronClinicalGenomicsData_node1665894278030 = ApplyMapping.apply(
    frame=ClinicoGenomicsDF_node1665689379027,
    mappings=[
        ("patient_id", "string", "patient_id", "string"),
        ("lab_specimen_identifier", "string", "lab_specimen_identifier", "string"),
        ("sample_type", "string", "sample_type", "string"),
        ("afr_ancestry_percent", "double", "afr_ancestry_percent", "double"),
        ("amr_ancestry_percent", "double", "amr_ancestry_percent", "double"),
        ("eas_ancestry_percent", "double", "eas_ancestry_percent", "double"),
        ("eur_ancestry_percent", "double", "eur_ancestry_percent", "double"),
        ("oce_ancestry_percent", "double", "oce_ancestry_percent", "double"),
        ("sas_ancestry_percent", "double", "sas_ancestry_percent", "double"),
        ("was_ancestry_percent", "double", "was_ancestry_percent", "double"),
    ],
    transformation_ctx="ApplyFilteronClinicalGenomicsData_node1665894278030",
)

# Script generated for node FilterProcedureData
FilterProcedureData_node1665694157838 = ApplyMapping.apply(
    frame=ProceduresDF_node1665690724543,
    mappings=[
        ("patient_id", "string", "pr_patient_id", "string"),
        ("claim_id", "string", "pr_claim_id", "string"),
        ("claim_type", "string", "pr_claim_type", "string"),
        ("procedure_date", "string", "pr_procedure_date", "string"),
        ("procedure_vocab", "string", "pr_procedure_vocab", "string"),
        ("procedure_code", "string", "pr_procedure_code", "string"),
        ("procedure_short_desc", "string", "procedure_short_desc", "string"),
        ("procedure_long_desc", "string", "procedure_long_desc", "string"),
        ("vocabulary_name", "string", "vocabulary_name", "string"),
    ],
    transformation_ctx="FilterProcedureData_node1665694157838",
)

# Script generated for node JoinClinicalGenomicswithProcedures
ApplyFilteronClinicalGenomicsData_node1665894278030DF = (
    ApplyFilteronClinicalGenomicsData_node1665894278030.toDF()
)
FilterProcedureData_node1665694157838DF = FilterProcedureData_node1665694157838.toDF()
JoinClinicalGenomicswithProcedures_node1665694145271 = DynamicFrame.fromDF(
    ApplyFilteronClinicalGenomicsData_node1665894278030DF.join(
        FilterProcedureData_node1665694157838DF,
        (
            ApplyFilteronClinicalGenomicsData_node1665894278030DF["patient_id"]
            == FilterProcedureData_node1665694157838DF["pr_patient_id"]
        ),
        "outer",
    ),
    glueContext,
    "JoinClinicalGenomicswithProcedures_node1665694145271",
)

# Script generated for node Join
JoinClinicalGenomicswithProcedures_node1665694145271DF = (
    JoinClinicalGenomicswithProcedures_node1665694145271.toDF()
)
RenamedkeysforJoin_node1665694312611DF = RenamedkeysforJoin_node1665694312611.toDF()
Join_node1665694288059 = DynamicFrame.fromDF(
    JoinClinicalGenomicswithProcedures_node1665694145271DF.join(
        RenamedkeysforJoin_node1665694312611DF,
        (
            JoinClinicalGenomicswithProcedures_node1665694145271DF["patient_id"]
            == RenamedkeysforJoin_node1665694312611DF["dg_patient_id"]
        ),
        "outer",
    ),
    glueContext,
    "Join_node1665694288059",
)

# Script generated for node finalJoin
Join_node1665694288059DF = Join_node1665694288059.toDF()
RenamedkeysforfinalJoin_node1665892999370DF = (
    RenamedkeysforfinalJoin_node1665892999370.toDF()
)
finalJoin_node1665891366375 = DynamicFrame.fromDF(
    Join_node1665694288059DF.join(
        RenamedkeysforfinalJoin_node1665892999370DF,
        (
            Join_node1665694288059DF["patient_id"]
            == RenamedkeysforfinalJoin_node1665892999370DF["rx_patient_id"]
        ),
        "outer",
    ),
    glueContext,
    "finalJoin_node1665891366375",
)

# Script generated for node Custom Transform
CustomTransform_node1665962473016 = MyTransform(
    glueContext,
    DynamicFrameCollection(
        {"finalJoin_node1665891366375": finalJoin_node1665891366375}, glueContext
    ),
)

# Script generated for node Select From Collection
SelectFromCollection_node1665962600856 = SelectFromCollection.apply(
    dfc=CustomTransform_node1665962473016,
    key=list(CustomTransform_node1665962473016.keys())[0],
    transformation_ctx="SelectFromCollection_node1665962600856",
)

# Script generated for node Amazon S3
AmazonS3_node1665695621571 = glueContext.write_dynamic_frame.from_options(
    frame=SelectFromCollection_node1665962600856,
    connection_type="s3",
    format="glueparquet",
    connection_options={
        "path": "s3://omics-datalake-genomics/phentotypic-datalake/",
        "partitionKeys": [],
    },
    transformation_ctx="AmazonS3_node1665695621571",
)

job.commit()
