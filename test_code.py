import cups

def check_job_status(job_id):
    # Get a connection to the CUPS server
    conn = cups.Connection()

    # Get information about the specific job
    job_info = conn.getJobs()

    # Check if the job_id exists in the job_info dictionary
    if job_id in job_info:
        # Get the status of the job
        job_status = job_info[job_id]['job-state']
        
        # Check if the job is completed
        if job_status == cups.JOB_COMPLETED:
            print(f"Job {job_id} is completed.")
        else:
            print(f"Job {job_id} is still in progress.")
    else:
        print(f"Job {job_id} not found.")

    # Close the connection
    conn.close()

# Example usage: Check the status of a specific job (replace 123 with the desired job ID)
check_job_status(123)
