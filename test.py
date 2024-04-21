button_labels = {
    'form_names': ['Individual Request of Petition Subject', 'Consolidated Requests of Petition Subject', 'Request on Shifting of Course',
                   'Thesis Distribution Form', 'Application for Subject Accreditation', 'Evaluation of Graduating Student with Academic Honors',
                   'List of Graduating Students with Academic Honors', 'List of Graduating Students with Loyalty Award', 'List of Graduating Students with Recognition Award',
                   'Form 1', 'Form 2', 'Form 3', 'Form 4', 'Form 5', 'Form 6', 'Form 7', 'Form 8', 'Form 9'
                   ],
    'form_types': ['Uncontrolled', 'Uncontrolled', 'Uncontrolled', 'Uncontrolled', 'Uncontrolled', 'Uncontrolled', 'Unctrolled', 'Uncontrolled', 'Uncontrolled',
                   'Controlled', 'Controlled', 'Controlled', 'Controlled', 'Controlled', 'Controlled', 'Controlled', 'Controlled', 'Controlled',
                   ],
    'num_of_page': [2, 1, 1, 1, 1, 3, 2, 2, 2, 1, 1, 1, 2, 2, 2, 1, 2, 3],
}

index = int(input("Enter the index: "))
if 0 <= index < len(button_labels['form_names']):
    form_name = button_labels['form_names'][index]
    form_type = button_labels['form_types'][index]
    num_of_pages = button_labels['num_of_page'][index]
    print(f"Form Name: {form_name}")
    print(f"Form Type: {form_type}")
    print(f"Number of Pages: {num_of_pages}")
else:
    print("Invalid index.")
