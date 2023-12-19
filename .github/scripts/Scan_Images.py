# import subprocess
# import pymongo
# import json
# from datetime import datetime

# # Read image names from the image.txt file in the config folder
# image_file_path = "config/image.txt"
# try:
#     with open(image_file_path, "r") as file:
#         image_names = [line.strip() for line in file.readlines()]
# except FileNotFoundError:
#     print(f"Error: Image file '{image_file_path}' not found.")
#     exit(1)

# # Connect to MongoDB
# client = pymongo.MongoClient("mongodb+srv://ratnesh:ratnesh@cluster0.3ka0uom.mongodb.net/cve_db?retryWrites=true&w=majority")
# today_date = datetime.now().strftime("%d-%m-%Y")
# collection_name = f"{today_date}_cve_list"
# db = client.cve_db
# collection = db[collection_name]

# for image_name in image_names:
#     try:
#         # Run Grype for each image and store the output in a variable
#         grype_output = subprocess.run(["grype", image_name, "-o", "json"], capture_output=True, text=True, check=True)

#         # Parse Grype output and delete existing data in MongoDB
#         collection.delete_many({"image": image_name})

#         # Insert the new data into MongoDB
#         grype_data = json.loads(grype_output.stdout)
#         matches = grype_data.get("matches", [])
#         for match in matches:
#             # Include the image name in the MongoDB document
#             match["image"] = image_name
#             match["message"] = "Vulnerability found."
#             collection.insert_one(match)

#         if not matches:
#             # Insert a message into MongoDB if no vulnerabilities found
#             collection.insert_one({"image": image_name, "message": "No vulnerabilities found."})
#             print(f"No vulnerability matches found in Grype output for {image_name}. Message inserted into MongoDB.")
#         else:
#             print(f"Data inserted into MongoDB for {image_name} successfully, Vulnerability found")
#     except subprocess.CalledProcessError as e:
#         print(f"Error running Grype for {image_name}: {e}")

import subprocess
import pymongo
import json
from datetime import datetime

# Read image names from the image.txt file in the config folder
image_file_path = "config/image.txt"
try:
    with open(image_file_path, "r") as file:
        image_names = [line.strip() for line in file.readlines()]
except FileNotFoundError:
    print(f"Error: Image file '{image_file_path}' not found.")
    exit(1)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://ratnesh:ratnesh@cluster0.3ka0uom.mongodb.net/cve_db?retryWrites=true&w=majority")
today_date = datetime.now().strftime("%d-%m-%Y")
collection_name = f"{today_date}_secure_images"
db = client.secure_images_db
collection = db[collection_name]

for image_name in image_names:
    try:
        # Perform tasks related to Initializ Secure Images
        # For example, pull the image with Docker
        subprocess.run(["docker", "pull", f"public.ecr.aws/{image_name}"])

        # Verify signature using cosign
        signature_verification = subprocess.run(
            [
                "cosign", "verify",
                f"public.ecr.aws/{image_name}",
                "--certificate-oidc-issuer", "https://token.actions.githubusercontent.com",
                "--certificate-identity", "https://github.com/initializ/secure-images/.github/workflows/release.yml@refs/heads/main"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        print(f"Signature verification for {image_name}:\n{signature_verification.stdout}")

        # Download SBOM using cosign
        sbom_download = subprocess.run(
            [
                "cosign", "download", "attestation",
                "--predicate-type", "https://spdx.dev/Document",
                f"public.ecr.aws/{image_name}"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        print(f"SBOM for {image_name}:\n{sbom_download.stdout}")

        # Insert a message into MongoDB indicating success
        collection.insert_one({"image": image_name, "message": "Tasks completed successfully."})
        print(f"Tasks completed successfully for {image_name}. Message inserted into MongoDB.")
    except subprocess.CalledProcessError as e:
        print(f"Error performing tasks for {image_name}: {e}")

