hos_addr = '10661'

disp_status_mapping = {
    '0': 'cancelled',
    '1': 'completed',
    '2': 'declined',
    '3': 'entered-in-error'
}

prd_code_flag = {
    '0': False,
    '1': False,
    '2': True,
    '3': True,
    '4': False,
    '5': True,
    '6': True,
    '7': False,
    '8': False,
    '9': False,
}

bill_muad_mapping = {
    "1": "https://sil-th.org/CSOP/standardCode",
    "2": "https://sil-th.org/CSOP/standardCode",
    "3": "https://tmt.this.or.th",
    "5": "https://sil-th.org/CSOP/standardCode",
    "6": "https://tmlt.this.or.th",
    "7": "https://tmlt.this.or.th",
    "8": "https://sil-th.org/CSOP/standardCode",
    "9": "https://sil-th.org/CSOP/standardCode",
    "A": "https://sil-th.org/CSOP/standardCode",
    "B": "https://sil-th.org/CSOP/standardCode",
    "C": "https://sil-th.org/CSOP/standardCode",
    "D": "https://sil-th.org/CSOP/standardCode",
    "E": "https://sil-th.org/CSOP/standardCode",
    "F": "https://sil-th.org/CSOP/standardCode",
    "G": "https://sil-th.org/CSOP/standardCode",
    "H": "https://sil-th.org/CSOP/standardCode",
    "I": "https://sil-th.org/CSOP/standardCode",
}


def create_bundle_resource(tran_items,disp_items,h_code,h_name):
    Alljson = list()
    combined_data = dict()
    for disp_id, info in disp_items.items():
        try:
            combined_data = {
                **info,
                **tran_items[info['inv_no']]
            }
        except KeyError:
            # print('There is error on', info['inv_no'])
            continue
        patient_identifiers = [
            {
                "system": "https://www.dopa.go.th",
                "value": f"{combined_data['pid']}"
            },
            {
                "system": "https://sil-th.org/CSOP/hn",
                "value": f"{combined_data['hn']}"
            }
        ]
        if combined_data['member_no'] != '':
            patient_identifiers.append({
                "system": "https://sil-th.org/CSOP/memberNo",
                "value": f"{combined_data['member_no']}"
            })
        sequence = 1
        claim_items = []
        for detail_disp_item in info['items']:
            item_combined_data = {
                **combined_data,
                **detail_disp_item
            }
            item_data = {
                "fullUrl": f"urn:uuid:MedicationDispense/{item_combined_data['disp_id']}/{item_combined_data['local_drug_id']}",
                "resource": {
                    "resourceType": "MedicationDispense",
                    "id" : f"{item_combined_data['local_drug_id']}",
                    "text": {
                        "status": "extensions",
                        "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Dispense ID: {item_combined_data['disp_id']} (HN: {item_combined_data['hn']})<p>{item_combined_data['dfs']} - {item_combined_data['instruction_text']}</p><p>QTY: {item_combined_data['quantity']} {item_combined_data['package_size']}</p></div>"
                    },
                    "extension": [
                        {
                            "url": "https://sil-th.org/fhir/StructureDefinition/product-category",
                            "valueCodeableConcept": {
                                "coding": [
                                    {
                                        "system": "https://sil-th.org/fhir/CodeSystem/csop-productCategory",
                                        "code": f"{item_combined_data['product_cat']}"
                                    }
                                ]
                            }
                        },
                    ],
                    "identifier": [
                        {
                            "system": "https://sil-th.org/CSOP/dispenseId",
                            "value": f"{item_combined_data['disp_id']}"
                        }
                    ],
                    "status": f"{disp_status_mapping[item_combined_data['disp_status']]}",
                    "category": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/fhir/CodeSystem/medicationdispense-category",
                                "code": "outpatient"
                            }
                        ]
                    },
                    "medicationCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://sil-th.org/CSOP/localCode",
                                "code": f"{item_combined_data['local_drug_id']}"
                            }
                        ],
                        "text": f"{item_combined_data['dfs']}"
                    },
                    "subject": {
                        "reference": f"urn:uuid:Patient/{h_code}/{item_combined_data['hn']}",
                    },
                    "context": {
                        "reference": f"urn:uuid:Encounter/D/{item_combined_data['disp_id']}"
                    },
                "performer": [
                        {
                            "actor": {
                                "reference": f"urn:uuid:Organization/{hos_addr}"
                            }
                        }
                    ],
                    "quantity": {
                        "value": float(item_combined_data['quantity']),
                        "unit": f"{item_combined_data['package_size']}"
                    },
                    "whenHandedOver": f"{item_combined_data['disp_date']}",
                    "dosageInstruction": [
                        {
                            "text": f"{item_combined_data['instruction_text']}",
                            "timing": {
                                "code": {
                                    "text": f"{item_combined_data['instruction_code']}"
                                }
                            }
                        }
                    ],
                },
                "request": {
                    "method": "PUT",
                    "url": f"MedicationDispense?identifier=https://sil-th.org/CSOP/dispenseId|{item_combined_data['disp_id']}&code=https://sil-th.org/CSOP/localCode|{item_combined_data['local_drug_id']}",
                    "ifNoneExist": f"identifier=https://sil-th.org/CSOP/dispenseId|{item_combined_data['disp_id']}&code=https://sil-th.org/CSOP/localCode|{item_combined_data['local_drug_id']}",
                }
            }
            sequence += 1
            claim_items.append(item_data)
        json_data = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": [
                {
                    "fullUrl": f"urn:uuid:Organization/{hos_addr}",
                    "resource": {
                        "resourceType": "Organization",
                        "id" : f"{hos_addr}",
                        "identifier": [
                            {
                                "system": "https://bps.moph.go.th/hcode/5",
                                "value": f"{h_code}"
                            }
                        ],
                        "name": f"{h_name}"
                    },
                    "request": {
                        "method": "PUT",
                        "url": f"Organization/{hos_addr}",
                        "ifNoneExist": f"identifier=https://bps.moph.go.th/hcode/5|{h_code}"
                    }
                },
                {
                    "fullUrl": f"urn:uuid:Patient/{h_code}/{combined_data['hn']}",
                    "resource": {
                        "resourceType": "Patient",
                        "id": f"{combined_data['hn']}",
                        "text": {
                            "status": "extensions",
                            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">{combined_data['name']} (HN: {combined_data['hn']})</div>"
                        },
                        "identifier": patient_identifiers,
                        "name": [
                            {
                                "text": f"{combined_data['name']}"
                            }
                        ],
                        "generalPractitioner": [
                            {
                                "type": "Organization",
                                "identifier": {
                                    "system": "https://bps.moph.go.th/hcode/5",
                                    "value": f"{h_code}"
                                }
                            }
                        ],
                        "managingOrganization": {
                            "reference": f"urn:uuid:Organization/{hos_addr}"
                        }
                    },
                    "request": {
                        "method": "PUT",
                        "url": f"Patient?identifier=https://sil-th.org/CSOP/hn|{combined_data['hn']}",
                        "ifNoneExist": f"identifier=https://sil-th.org/CSOP/hn|{combined_data['hn']}"
                    }
                },
                {
                    "fullUrl": f"urn:uuid:Location/{combined_data['station']}",
                    "resource": {
                        "resourceType": "Location",
                        "id" :f"{combined_data['station']}",
                        "text": {
                            "status": "generated",
                            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Station ID: {combined_data['station']}</div>"
                        },
                        "identifier": [
                            {
                                "system": "https://sil-th.org/CSOP/station",
                                "value": f"{combined_data['station']}"
                            }
                        ],
                        "type": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                                        "code": "BILL",
                                        "display": "Billing Contact"
                                    }
                                ]
                            }
                        ],
                        "managingOrganization": {
                            "reference": f"urn:uuid:Organization/{hos_addr}"
                        }
                    },
                    "request": {
                        "method": "PUT",
                        "url": f"Location?identifier=https://sil-th.org/CSOP/station|{combined_data['station']}",
                        "ifNoneExist": f"identifier=https://sil-th.org/CSOP/station|{combined_data['station']}"
                    }
                },
                {
                    "fullUrl": f"urn:uuid:Practitioner/{combined_data['practitioner']['type']}/{combined_data['license_id'][1:]}",
                    "resource": {
                        "resourceType": "Practitioner",
                        "id" : f"{combined_data['license_id'][1:]}",
                        "text": {
                            "status": "extensions",
                            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">{combined_data['license_id']}</div>"
                        },
                        "identifier": [
                            {
                                "type": {
                                    "coding": [
                                        {
                                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                            "code": f"{combined_data['practitioner']['type']}"
                                        }
                                    ]
                                },
                                "system": f"{combined_data['practitioner']['system']}",
                                "value": f"{combined_data['license_id'][1:]}"
                            }
                        ]
                    },
                    "request": {
                        "method": "PUT",
                        "url": f"Practitioner?identifier={combined_data['practitioner']['system']}|{combined_data['license_id'][1:]}",
                        "ifNoneExist": f"identifier={combined_data['practitioner']['system']}|{combined_data['license_id'][1:]}"
                    }
                },
                {
                    "fullUrl": f"urn:uuid:Encounter/D/{combined_data['disp_id']}",
                    "resource": {
                        "resourceType": "Encounter",
                        "id" : f"{combined_data['disp_id']}",
                        "text": {
                            "status": "extensions",
                            "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Dispense ID: {combined_data['disp_id']} (HN: {combined_data['hn']})<p>service: Pharmacy | status: {disp_status_mapping[combined_data['disp_status']]}</p></div>"
                        },
                        "identifier": [
                            {
                                "system": "https://sil-th.org/CSOP/dispenseId",
                                "value": f"{combined_data['disp_id']}"
                            }
                        ],
                        "status": "finished",
                        "class": {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                            "code": "AMB"
                        },
                        "serviceType": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/service-type",
                                    "code": "64",
                                    "display": "Pharmacy"
                                }
                            ]
                        },
                        "subject": {
                            "reference": f"urn:uuid:Patient/{h_code}/{combined_data['hn']}"
                        },
                        "participant": [
                            {
                                "individual": {
                                    "reference": f"urn:uuid:Practitioner/{combined_data['practitioner']['type']}/{combined_data['license_id'][1:]}"
                                }
                            }
                        ],
                        "period": {
                            "start": f"{combined_data['presc_date']}",
                            "end": f"{combined_data['disp_date']}"
                        },
                        "serviceProvider": {
                            "reference": f"urn:uuid:Organization/{hos_addr}"
                        },
                    },
                    "request": {
                        "method": "PUT",
                        "url": f"Encounter?identifier=https://sil-th.org/CSOP/dispenseId|{combined_data['disp_id']}",
                        "ifNoneExist": f"identifier=https://sil-th.org/CSOP/dispenseId|{combined_data['disp_id']}"
                    }
                },
            ]
        }
        json_data['entry'].extend(claim_items)
        Alljson.append(json_data)
    return Alljson
        
