import os
import glob
import shutil
from pdf2image import convert_from_path


def rename_file(destination_path, new_form_name):
    try:
        os.rename(destination_path, new_form_name)
    except OSError as e:
        print("Error renaming file:", e)


def delete_form_file(form_name):
    """
    Deletes a form file from the 'forms' directory.
    """
    destination_path = os.path.join("./forms", f"{form_name}.pdf")

    if os.path.exists(destination_path):
        try:
            os.remove(destination_path)
            print(f"File deleted successfully.")
        except OSError as e:
            print("Error deleting file:", e)
    else:
        print("No file found to delete.")


def delete_process_file(form_name):
    """
    Deletes process files related to a form.
    """
    process_files = glob.glob(f"./img/process/{form_name}.*")

    if not process_files:
        print("No file found to delete.")
        return

    for file_path in process_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File {file_path} deleted successfully.")
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")


def delete_form_preview(form_name):
    """
    Deletes form preview images.
    """
    form_preview_files = glob.glob(f"./img/form-preview/{form_name}-*.jpg")

    if not form_preview_files:
        print("No file found to delete.")
        return

    for file_path in form_preview_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File {file_path} deleted successfully.")
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")


def upload_form_file(filepath, form_title):
    """
    Uploads a form file to the 'forms' directory and converts it to JPEG.
    """
    destination_directory = "./forms"
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File '{filepath}' does not exist.")

        if not os.path.isfile(filepath):
            raise ValueError(f"'{filepath}' is not a file.")

        filename = os.path.basename(filepath)
        file_extension = os.path.splitext(filename)[1]
        destination_path = os.path.join(destination_directory, filename)

        if os.path.exists(destination_path):
            os.remove(destination_path)

        shutil.copy(filepath, destination_path)
        print(f"File '{filename}' uploaded to '{destination_path}'")

        new_form_name = os.path.join(
            destination_directory, f"{form_title}{file_extension}"
        )
        rename_file(destination_path, new_form_name)
        convert_pdf_to_jpg(new_form_name, form_title)

    except Exception as e:
        print("Error uploading file:", e)


def edit_form_file(filepath, form_title, form_name):
    """
    Edits a form file by deleting old versions and uploading a new one.
    """
    destination_directory = "./forms"
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File '{filepath}' does not exist.")

        if not os.path.isfile(filepath):
            raise ValueError(f"'{filepath}' is not a file.")

        filename = os.path.basename(filepath)
        file_extension = os.path.splitext(filename)[1]
        destination_path = os.path.join(destination_directory, filename)

        delete_form_file(form_name)
        delete_form_preview(form_name)

        shutil.copy(filepath, destination_path)
        print(f"File '{filename}' uploaded to '{destination_path}'")

        new_form_name = os.path.join(
            destination_directory, f"{form_title}{file_extension}"
        )
        rename_file(destination_path, new_form_name)
        convert_pdf_to_jpg(new_form_name, form_title)

    except Exception as e:
        print("Error uploading file:", e)


def upload_process_file(filepath, form_title):
    """
    Uploads a process file and renames it.
    """
    destination_directory = "./img/process"
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File '{filepath}' does not exist.")

        if not os.path.isfile(filepath):
            raise ValueError(f"'{filepath}' is not a file.")

        filename = os.path.basename(filepath)
        file_extension = os.path.splitext(filename)[1]
        destination_path = os.path.join(destination_directory, filename)

        if os.path.exists(destination_path):
            os.remove(destination_path)

        shutil.copy(filepath, destination_path)
        print(f"File '{filename}' uploaded to '{destination_path}'")

        new_process_name = os.path.join(
            destination_directory, f"{form_title}{file_extension}"
        )
        rename_file(destination_path, new_process_name)

    except Exception as e:
        print("Error uploading file:", e)


def edit_process_file(filepath, form_title, form_name):
    """
    Edits a process file by deleting old versions and uploading a new one.
    """
    destination_directory = "./img/process"
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File '{filepath}' does not exist.")

        if not os.path.isfile(filepath):
            raise ValueError(f"'{filepath}' is not a file.")

        filename = os.path.basename(filepath)
        file_extension = os.path.splitext(filename)[1]
        destination_path = os.path.join(destination_directory, filename)

        delete_process_file(form_name)

        shutil.copy(filepath, destination_path)
        print(f"File '{filename}' uploaded to '{destination_path}'")

        new_process_name = os.path.join(
            destination_directory, f"{form_title}{file_extension}"
        )
        rename_file(destination_path, new_process_name)

    except Exception as e:
        print("Error uploading file:", e)


def convert_pdf_to_jpg(pdf_path, form_title):
    """
    Converts a PDF file to JPEG images.
    """
    destination_folder = "./img/form-preview"

    pages = convert_from_path(pdf_path)

    for i, page in enumerate(pages):
        page.save(f"{destination_folder}/{form_title}-{i+1}.jpg", "JPEG")
