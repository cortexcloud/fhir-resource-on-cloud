import math
import os

from datetime import datetime
from dotenv import load_dotenv
from fhir_transformer.csop.xml_extractor import _open_bill_trans_xml, _open_bill_disp_xml
from fhir_transformer.csop.bundle_package import create_bundle_resource
from fhir_transformer.csop.gcp_connector import import_files_to_bucket,import_fhir_resources


load_dotenv()

def process(bill_trans_xml_path: str, bill_disp_xml_path: str, import_time: datetime, set_no: int):
    # Import Environment Variable
    project_id = os.getenv('PROJECT_ID')
    location = os.getenv('LOCATION')
    dataset_id = os.getenv('DATASET_ID')
    fhir_store_id = os.getenv('FHIR_STORE_ID')
    gcs_bucket_name = os.getenv('GCP_BUCKET_NAME')
    gcp_bucket_folder = os.getenv('GCP_BUCKET_FOLDER')
    credential_path = os.getenv('CREDENTIAL_PATH')
    # Open CSOP xml Files
    bill_trans_xml_data,h_code,h_name = _open_bill_trans_xml(bill_trans_xml_path)
    bill_disp_xml_data = _open_bill_disp_xml(bill_disp_xml_path)
    # Set Up File Path on GCS
    files_path = f"{gcp_bucket_folder}/{import_time}/{set_no}"
    gcs_path = f"{gcs_bucket_name}/{files_path}/*"
    # Prepare Bundle Resource From XML
    bundle_resource = create_bundle_resource(bill_trans_xml_data,bill_disp_xml_data,h_code,h_name)
    # Send Bundle Json To GCS 
    import_files_to_bucket(files_path,bundle_resource,credential_path)
    # Call GCP API to Import Json to FHIR server
    import_fhir_resources(project_id,location,dataset_id,fhir_store_id,gcs_path,credential_path)