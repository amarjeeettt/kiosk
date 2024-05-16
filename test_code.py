import subprocess

def is_job_completed(job_id):
    try:
        completed_jobs_output = subprocess.check_output(["lpstat", "-W", "completed", "-o"]).decode("utf-8")
        completed_jobs_output_lines = completed_jobs_output.split("\n")
        for line in completed_jobs_output_lines:
            if job_id in line:
                return True
        return False
    except subprocess.CalledProcessError as e:
        print("Error executing lpstat command:", e)
        return False

# Usage example:
job_id = "217"
if is_job_completed(job_id):
    print(f"Job {job_id} is completed.")
else:
    print(f"Job {job_id} is not completed.")


