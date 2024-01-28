from django.core.management import BaseCommand
import getpass
import os
import subprocess
import pyminizip
from datetime import datetime

class Command(BaseCommand):
    help = 'Creates a password-protected database dump'

    def handle(self, *args, **options):
        # Prompt the user for a password
        password = getpass.getpass('Enter the password for the database dump: ')

        # Create a directory named "dumps" if it doesn't exist
        os.makedirs('dumps', exist_ok=True)

        # Use Django's dumpdata to create a JSON file with all the data from your application
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Get current date and time
        dump_file = f"dumps/db_dump_{timestamp}.json"  # Append timestamp to filename
        subprocess.call(f"python manage.py dumpdata poll_app > {dump_file}", shell=True)

        # Use pyminizip to create a password-protected zip file containing the JSON file
        zip_file = f"dumps/db_dump_{timestamp}.zip"  # Append timestamp to filename
        pyminizip.compress(dump_file, None, zip_file, password, 0)

        # Delete the original dump file
        os.remove(dump_file)

        self.stdout.write(self.style.SUCCESS('Successfully created database dump'))