import json

from googleapiclient import discovery
from google.cloud import storage
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

def create_json(json_object, filename, storage_client, bucket_name):
    '''
    this function will create json object in
    google cloud storage
    '''
    BUCKET = storage_client.get_bucket(bucket_name)
    # create a blob
    blob = BUCKET.blob(filename)
    # upload the blob 
    blob.upload_from_string(
        data=json.dumps(json_object),
        content_type='application/json'
        )
    result = filename + ' upload complete'
    return {'response' : result}

def import_files_to_bucket(files_path, json_data, gcs_bucket_name, credential_path):
    storage_client = storage.Client.from_service_account_json(credential_path)
    # write your bucket name in place of bucket1go
    for i in range(len(json_data)):
        # your object
        json_object = json_data[i]
        # set the filename of your json object
        filename = f'{files_path}/SBH_'+str(i)+'.json'
        # run the function and pass the json_object
        print(create_json(json_object, filename, storage_client, gcs_bucket_name))
    print('Import Json to GCS Successfully')

def import_fhir_resources(project_id, location, dataset_id, fhir_store_id, gcs_uri, credential_path):
    """Import resources into the FHIR store by copying them from the
    specified source.
    See https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/healthcare/api-client/v1/fhir
    before running the sample."""

    api_version = "v1"
    service_name = "healthcare"
    # Instantiates an authorized API client by discovering the Healthcare API
    # and using GOOGLE_APPLICATION_CREDENTIALS environment variable.
    credentials = service_account.Credentials.from_service_account_file(credential_path)
    client = discovery.build(service_name, api_version, credentials=credentials)

    # TODO(developer): Uncomment these lines and replace with your values.
    # project_id = 'my-project'  # replace with your GCP project ID
    # location = 'us-central1'  # replace with the parent dataset's location
    # dataset_id = 'my-dataset'  # replace with the parent dataset's ID
    # fhir_store_id = 'my-fhir-store'  # replace with the FHIR store ID
    # gcs_uri = 'my-bucket'  # replace with a Cloud Storage bucket
    fhir_store_parent = "projects/{}/locations/{}/datasets/{}".format(
        project_id, location, dataset_id
    )
    fhir_store_name = "{}/fhirStores/{}".format(fhir_store_parent, fhir_store_id)
    
    body = {
        "contentStructure": "BUNDLE_PRETTY",
        "gcsSource": {"uri": "gs://{}".format(gcs_uri)},
    }
    print(body)

    # Escape "import()" method keyword because "import"
    # is a reserved keyword in Python
    request = (
        client.projects()
        .locations()
        .datasets()
        .fhirStores()
        .import_(name=fhir_store_name, body=body)
    )

    response = request.execute()
    print("Imported FHIR resources Successfully: {}".format(gcs_uri))

    return response


