import os
import boto3
import botocore
import sys


def main():
    promptUser()


s3 = boto3.resource("s3")
s3_client = boto3.client("s3")
buckets = s3.buckets.all()


def printBuckets():
    for bucket in buckets:
        print(bucket.name)
        for key in bucket.objects.all():
            print(key.key)

# newBucket = input("New Bucket Name: ")

# print("Creating bucket: ", newBucket)

# s3_connection = boto3.connect_s3()

# creates a new bucket and loops to beginning if the bucket name inputted is invalid
def createNewBucket(directoryName):
    newBucket = input("New Bucket Name: ")
    toreturn = newBucket
    try:
        print("Attempting to create bucket: ", newBucket)
        s3.create_bucket(CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}, Bucket=newBucket)
        backup(newBucket, directoryName)
    except:
        print("Something went wrong. Try again")
        createNewBucket(directoryName)

    return toreturn

# checks if a bucket already exists
def findExistingBucket(existingBucket):
    for bucket in s3.buckets.all():
        if bucket.name == existingBucket:
            # bucket found
            print("bucket found")
            return True
        else:
            print("Bucket not found")
    return False

# prompts the user to input necessary information
def promptUser():
    directory_name = sys.argv[1]
    if len(sys.argv) != 2:
        print("Too many arguments, exiting.")
        sys.exit()
    # directory_name = input("Directory name: ")
    if not os.path.exists(directory_name):
        print("Invalid Directory. Exiting.")
        sys.exit()
    backup_or_restore = input("Do you want to backup or restore[backup/restore]: ")
    if backup_or_restore == "backup":
        existing_or_new = input("Do you want to backup to an existing or new bucket[existing/new]: ")
        if existing_or_new == "new":
            backu = createNewBucket(directory_name)
            # print("Bucket name: " + backu)
            # backup(backu, directory_name)

        if existing_or_new == "existing":
            existingBucket = input("Existing Bucket Name: ")
            if findExistingBucket(existingBucket):
                print("Backing up to: " + existingBucket)
                backup(existingBucket, directory_name)
            else:
                print("Bucket not found. Not backing up.")
        else:
            # print("Invalid input. Exiting.")
            sys.exit()
    if backup_or_restore == "restore":
        existingBucket = input("Existing Bucket Name: ")
        if findExistingBucket(existingBucket):
            print("Starting restoration")
            restore(existingBucket, directory_name)
        if not findExistingBucket(existingBucket):
            print("Existing bucket not found, cannot restore")
    else:
        # print("Invalid input. Exiting.")
        sys.exit()

# method that backs up specified directory into the specified bucket name
def backup(bucketName, directory_name):
    print("Starting backup...")
    for path, subdirs, files in os.walk(directory_name):
        path = path.replace("\\", "/")
        for file in files:
            local_directory = os.path.join(path, file)
            relative_directory = os.path.relpath(local_directory, directory_name)
            relative_directory = relative_directory.replace("\\", "/")
            try:
                s3.Object(bucketName, relative_directory).load()
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    s3.Bucket(bucketName).upload_file(local_directory, relative_directory)
                else:
                    raise
            else:
                if(int(s3.Object(bucketName, relative_directory).last_modified.timestamp())) < int(os.path.getmtime(local_directory)):
                    s3.Bucket(bucketName).upload_file(local_directory, relative_directory)
                else:
                    print("Backup is up tp date")

    print("Directory Backed Up!")

# method that restores items from a bucket into a local directory
def restore(bucketName, local):
    your_bucket = s3.Bucket(bucketName)
    for objectFile in your_bucket.objects.all():
        file = os.path.join(local, objectFile.key.replace('/', '\\'))
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))
        your_bucket.download_file(objectFile.key, file)

    print("Restoration Successfull")



# backup(directory_name)

# restore("C:/Users/Omar Iqbal/Desktop/testfors3/")

main()