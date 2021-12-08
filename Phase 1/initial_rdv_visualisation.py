from common_routines import *

def create_rdv_demographics(outfilepath, plist_filepath, number_patients = 10, birth_date_start_date=None,
                            birth_date_end_date=None, death_percentage=0.0):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    # project_id,hospital_no,birth_date,death_date,deceased_flag,sex,ethnicity_nat_code,ethnicity_local_code,ethnicity_name
    # First do RDV summary
    # Output the file

    log_debug("Creating RDV: {0}, patient list: {1}".format(outfilepath, plist_filepath))

    if birth_date_start_date is None:
        birth_date_start_date = date(2010, 1, 1)
    if birth_date_end_date is None:
        birth_date_end_date = date(2021, 5, 31)

    high = (birth_date_end_date - birth_date_start_date).days
    birth_date_choices = np.random.randint(0, high, number_patients)

    p = []
    p.append(1-death_percentage)
    p.append(death_percentage)
    death_choices = np.random.choice([0,1], number_patients, replace=True, p=p)

    sex_choices = np.random.choice(["F", "M"], number_patients, replace=True, p=[0.5, 0.5])

    # Get ethnicity codes:
    number_codes = 5
    ethnicity_choices = np.random.choice([1,2,3,4,5], number_patients, replace=True, p=[0.6, 0.2, 0.1, 0.05, 0.05])

    with open(outfilepath, 'w', newline='') as ofile_handle, open(plist_filepath, 'w', newline='') as pfile_handle:

        writer = csv.writer(ofile_handle)
        p_writer = csv.writer(pfile_handle)

        # output header - demographics
        output_row = []
        output_row.append("project_id")
        output_row.append("hospital_no")
        output_row.append("birth_date")
        output_row.append("death_date")
        output_row.append("deceased_flag")
        output_row.append("sex")
        output_row.append("ethnicity_nat_code")
        output_row.append("ethnicity_local_code")
        output_row.append("ethnicity_name")
        writer.writerow(output_row)

        # output header - patient_list
        output_row = []
        output_row.append("project_id")
        output_row.append("hospital_no")
        output_row.append("start_datetime")
        output_row.append("end_datetime")
        p_writer.writerow(output_row)

        for patient_num in range(0, number_patients):

            sys.stdout.write("\r \rProcessing rows: {0} of {1}".format(patient_num + 1, number_patients))
            sys.stdout.flush()

            project_id = "PR-" + str(1000000 + (patient_num + 1))[1:]
            hospital_no = str(100000 + (patient_num + 1))
            birth_date = birth_date_start_date + timedelta(days=int(birth_date_choices[patient_num]))

            if death_choices[patient_num] == 0:
                death_date = ""
                deceased_flag = "N"
            else:
                high = (date.today() - birth_date).days
                life_days = int(np.random.randint(1, high))
                death_date = (birth_date + timedelta(days=life_days)).strftime("%Y-%m-%d")
                deceased_flag = "Y"

            sex = sex_choices[patient_num]
            ethnicity_nat_code = f"ET{ethnicity_choices[patient_num]}"
            ethnicity_local_code = f"ET{ethnicity_choices[patient_num]}"
            ethnicity_name = f"Ethnicity {ethnicity_choices[patient_num]}"

            output_row = []
            output_row.append(project_id)
            output_row.append(hospital_no)
            output_row.append(birth_date.strftime("%Y-%m-%d"))
            output_row.append(death_date)
            output_row.append(deceased_flag)
            output_row.append(sex)
            output_row.append(ethnicity_nat_code)
            output_row.append(ethnicity_local_code)
            output_row.append(ethnicity_name)
            writer.writerow(output_row)

            # patient_list
            output_row = []
            output_row.append(project_id)
            output_row.append(hospital_no)
            output_row.append("")
            output_row.append("")
            p_writer.writerow(output_row)

        print()

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))


def create_rdv_hospital_admissions(outfilepath, demographics_filepath, plist_filepath, ha_start_date=None, ha_end_date=None, ha_min_stay=7, ha_max_stay=14):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    '''
    To be added:
    1. More than one stay in hospital for a patient
    2. Add codes
    '''

    # project_id,encounter_key,patient_class,hospital_service,admission_type,admission_source,disharge_disposition,principal_problem,start_datetime,end_datetime

    # read in patient demographics
    log_debug("Reading Demographics: {0}".format(demographics_filepath))

    df_patient_demographics = pd.read_csv(demographics_filepath)
    number_patients = len(df_patient_demographics.index)

    log_debug("Creating RDV: {0}".format(outfilepath))

    if ha_start_date is None:
        ha_start_date = date(2019, 5, 1)
    if ha_end_date is None:
        ha_end_date = date(2021, 5, 31)

    # Done by patient as depends on birth_date
    # high = (ha_end_date - ha_start_date).days
    # ha_day_choices = np.random.randint(0, high, number_patients)
    #
    ha_los_choices = np.random.randint(ha_min_stay, ha_max_stay, number_patients)

    start_time_choices = np.random.normal(loc=(12*60), scale=(4*60), size=number_patients)
    end_time_choices = np.random.normal(loc=(12*60), scale=(4*60), size=number_patients)

    # Get encounter_keys:
    encounter_choices = np.random.choice(1000000, number_patients, replace=False)

    with open(outfilepath, 'w', newline='') as ofile_handle, open(plist_filepath, 'w', newline='') as pfile_handle:

        writer = csv.writer(ofile_handle)
        p_writer = csv.writer(pfile_handle)

        # output header
        output_row = []
        output_row.append("project_id")
        output_row.append("encounter_key")
        output_row.append("patient_class")
        output_row.append("hospital_service")
        output_row.append("admission_type")
        output_row.append("admission_source")
        output_row.append("disharge_disposition")
        output_row.append("principal_problem")
        output_row.append("start_datetime")
        output_row.append("end_datetime")
        writer.writerow(output_row)

        # output header - patient_list
        output_row = []
        output_row.append("project_id")
        output_row.append("hospital_no")
        output_row.append("start_datetime")
        output_row.append("end_datetime")
        p_writer.writerow(output_row)

        for patient_num, row in df_patient_demographics.iterrows():

            sys.stdout.write("\r \rProcessing rows: {0} of {1}".format(patient_num + 1, number_patients))
            sys.stdout.flush()

            project_id = row['project_id']
            hospital_no = row['hospital_no']
            birth_date = return_date(row['birth_date'])

            encounter_key = 1000000 + encounter_choices[patient_num]

            # Get a start_date for patient must ne greater than their birth date!
            pa_start_date = ha_start_date if ha_start_date >= birth_date.date() else birth_date.date()
            high = (ha_end_date - pa_start_date).days
            ha_start_day = np.random.randint(0, high)

            los_days = int(ha_los_choices[patient_num])
            start_datetime = datetime.combine((pa_start_date + timedelta(days=ha_start_day)), datetime.min.time()) + timedelta(minutes=int(start_time_choices[patient_num]))
            end_datetime = datetime.combine((start_datetime + timedelta(days=los_days)), datetime.min.time()) + timedelta(minutes=int(end_time_choices[patient_num]))

            output_row = []
            output_row.append(project_id)
            output_row.append(encounter_key)
            output_row.append("")
            output_row.append("")
            output_row.append("")
            output_row.append("")
            output_row.append("")
            output_row.append("")
            output_row.append(start_datetime.strftime("%Y-%m-%d %H:%M"))
            output_row.append(end_datetime.strftime("%Y-%m-%d %H:%M"))
            writer.writerow(output_row)

            # patient_list
            output_row = []
            output_row.append(project_id)
            output_row.append(hospital_no)
            output_row.append(start_datetime.strftime("%Y-%m-%d %H:%M"))
            output_row.append(end_datetime.strftime("%Y-%m-%d %H:%M"))
            p_writer.writerow(output_row)

        print()

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))


def create_dt_drug_hierachy(number_drugs=100, number_pharmsubclass=25, number_pharmclass = 10, max_doses_per_day=3, 
                         min_admin_days=1, max_admin_days=3):

    log_debug("Creating a drug list")

    # Limited in the code below
    max_doses_per_day = 5 if max_doses_per_day > 5 else max_doses_per_day

    # Create heirachy
    # pharm class - number
    # pharm subclass - number - allocate to pharm class
    # drugs - number - allocate to pharm subclass
    #
    # number of doses per day
    # number of days

    # for each drug
    # decide which

    dt_drug_hierachy = dict()
    dt_drug_hierachy['pharmclasses'] = dict()
    dt_drug_hierachy['pharmsubclasses'] = dict()
    dt_drug_hierachy['drugs'] = dict() 

    for pharmclass_num in range(1, number_pharmclass + 1):
        # Assign pharmsubclass to class
        dt_drug_hierachy['pharmclasses'][pharmclass_num] = dict()
        dt_drug_hierachy['pharmclasses'][pharmclass_num]['name'] = f"Drug pharmaceutical class {pharmclass_num}"
        dt_drug_hierachy['pharmclasses'][pharmclass_num]['pharmsubclasses'] = []

    for pharmsubclass_num in range(1, number_pharmsubclass + 1):
        # Assign pharmsubclass to class
        pharmclass_num = 1 + np.random.choice(number_pharmclass, replace =True)
        dt_drug_hierachy['pharmclasses'][pharmclass_num]['pharmsubclasses'].append(pharmsubclass_num)
        dt_drug_hierachy['pharmsubclasses'][pharmsubclass_num] = dict()
        dt_drug_hierachy['pharmsubclasses'][pharmsubclass_num]['name'] = f"Drug pharmaceutical subclass {pharmsubclass_num}"
        dt_drug_hierachy['pharmsubclasses'][pharmsubclass_num]['drugs'] = []
        dt_drug_hierachy['pharmsubclasses'][pharmsubclass_num]['pharmclass'] = pharmclass_num

    for drug_num in range(1,number_drugs + 1):
        # Assign drug to subclass
        pharmsubclass_num = 1 + np.random.choice(number_pharmsubclass, replace =True)
        dt_drug_hierachy['pharmsubclasses'][pharmsubclass_num]['drugs'].append(drug_num)
        dt_drug_hierachy['drugs'][drug_num] = dict()
        dt_drug_hierachy['drugs'][drug_num]['pharmsubclass'] = pharmsubclass_num
        # Assign other drug variables
        # Number of doses per day
        doses_per_day = 1 + np.random.choice(max_doses_per_day, replace=True)
        dt_drug_hierachy['drugs'][drug_num]['doses_per_day'] = doses_per_day
        # Number of days
        admin_days = 1 + np.random.choice(max_admin_days, replace=True)
        admin_days = admin_days if admin_days >= min_admin_days else min_admin_days
        dt_drug_hierachy['drugs'][drug_num]['admin_days'] = admin_days
        dt_drug_hierachy['drugs'][drug_num]['drug_code'] = f"DG{drug_num}"
        dt_drug_hierachy['drugs'][drug_num]['drug_name'] = f"Drug {drug_num}, Doses: {doses_per_day}, Admin days: {admin_days}"
        dt_drug_hierachy['drugs'][drug_num]['drug_simple_generic_name'] = f"Drug {drug_num}"

    return dt_drug_hierachy

def create_rdv_medication_orders(outfilepath, hospital_admissions_filepath, dt_drug_hierachy, max_orders_per_day=12):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    '''
    To be added:
    1. check order and admin datetimes all within hospital admin datetimes
    '''

    # project_id,start_datetime,end_datetime,MedicationOrderKey,ordered_datetime,medication_order_id,sequence_number,
    # drug_code,drug_name,drug_gpi,drug_simple_generic_name,drug_therapeutic_class_name,drug_pharmaceutical_class_name,
    # drug_pharmaceutical_subclass_name,dose_amount,formulation_code,intended_frequency,quantity,dose,dose_range,
    # calculated_dose_range,dose_number,route_name,indication,indication_comments,response,medication_order_name,
    # medication_order_mode_name,medication_order_class_name,medication_order_source_name,disps_this_period,
    # admins_this_period,first_admin_datetime,encounter_key

    number_drugs = len(dt_drug_hierachy["drugs"])

    # read in patient demographics
    log_debug("Reading Hospital Admissions: {0}".format(hospital_admissions_filepath))

    df_hospital_admissions = pd.read_csv(hospital_admissions_filepath)
    number_admissions = len(df_hospital_admissions.index)

    log_debug("Creating RDV: {0}".format(outfilepath))

    # keep track on which drug is being administered on each day so no duplicates
    drug_administrations = dict()

    with open(outfilepath, 'w', newline='') as ofile_handle:

        writer = csv.writer(ofile_handle)

        # output header
        output_row = []
        output_row.append("project_id")
        output_row.append("start_datetime")
        output_row.append("end_datetime")
        output_row.append("MedicationOrderKey")
        output_row.append("ordered_datetime")
        output_row.append("medication_order_id")
        output_row.append("sequence_number")
        output_row.append("drug_code")
        output_row.append("drug_name")
        output_row.append("drug_gpi")
        output_row.append("drug_simple_generic_name")
        output_row.append("drug_therapeutic_class_name")
        output_row.append("drug_pharmaceutical_class_name")
        output_row.append("drug_pharmaceutical_subclass_name")
        output_row.append("encounter_key")
        writer.writerow(output_row)

        number_medication_orders = 0
        number_medication_admins = 0

        for patient_num, row in df_hospital_admissions.iterrows():

            sys.stdout.write("\r \rProcessing rows: {0} of {1}, Medication orders: {2}, admins: {3}".format(patient_num + 1,
                                                                                               number_admissions,
                                                                                               number_medication_orders,
                                                                                               number_medication_admins))
            sys.stdout.flush()

            project_id = row['project_id']
            ha_start_datetime = return_date(row['start_datetime'])
            ha_end_datetime = return_date(row['end_datetime'])
            num_days_admission = (ha_end_datetime - ha_start_datetime).days + 1
            encounter_key = row['encounter_key']

            drug_administrations[project_id] = dict()

            for day_num in range(0,num_days_admission):
                drug_administrations[project_id][day_num] = dict()

            # For each day in the admission
            #   get a number of medication orders
            #   for each medication order on a given day
            #     get a drug - must not already being administered
            #     for a given drug get number of doses per day and the number of days
            for day_num in range(0,num_days_admission):
                # log_debug(f"day_num: {day_num}")
                # How many medication orders today?
                num_medication_orders = 1 + np.random.choice(max_orders_per_day, replace=True)
                MedicationOrderKeys = np.random.choice(1000000, size=num_medication_orders, replace=False)
                medication_order_ids = np.random.choice(1000000, size=num_medication_orders, replace=False)
                for medication_order_num in range(0,num_medication_orders):
                    # log_debug(f"medication_order_num: {medication_order_num}")
                    number_medication_orders += 1
                    MedicationOrderKey = 1000000 + MedicationOrderKeys[medication_order_num]
                    medication_order_id = 1000000 + medication_order_ids[medication_order_num]
                    # get a drug for this order that is not already in use
                    drug_num = -1
                    while drug_num < 0 or drug_num in drug_administrations[project_id][day_num]:
                        # Maybe add a counter in here to check not in endless loop as no more drugs?
                        drug_num = 1 + np.random.choice(number_drugs, replace=True)
                    # for a given drug get number of doses per day and the number of days
                    doses_per_day = dt_drug_hierachy['drugs'][drug_num]['doses_per_day']
                    admin_days = dt_drug_hierachy['drugs'][drug_num]['admin_days']
                    start_datetime = ha_start_datetime + timedelta(days=day_num)
                    for admin_day_num in range(day_num,day_num + admin_days + 1):
                        if admin_day_num in drug_administrations[project_id]:
                            # log_debug(f"admin_day_num: {admin_day_num}")
                            drug_administrations[project_id][admin_day_num][drug_num] = dict()
                            drug_administrations[project_id][admin_day_num][drug_num]['doses_per_day'] = doses_per_day
                            drug_administrations[project_id][admin_day_num][drug_num]['MedicationOrderKey'] = MedicationOrderKey
                            drug_administrations[project_id][admin_day_num][drug_num]['medication_order_id'] = medication_order_id
                            if admin_day_num == 0: # if start of day of admission
                                admin_start_datetime = ha_start_datetime + timedelta(days=admin_day_num)
                            else:
                                # first admin of the day will be 06:00 then 10:00, 14:00, 18:00, 22:00 - check not already discharged
                                admin_start_datetime = datetime.combine(ha_start_datetime.date(), datetime.min.time()) + \
                                                 timedelta(minutes=int(6*60)) + timedelta(days=admin_day_num)
                            drug_administrations[project_id][admin_day_num][drug_num]['start_datetime'] = admin_start_datetime

                            number_medication_admins += doses_per_day
                    # Add medication order:
                    drug_code = dt_drug_hierachy['drugs'][drug_num]['drug_code']
                    drug_name = dt_drug_hierachy['drugs'][drug_num]['drug_name']
                    drug_simple_generic_name = dt_drug_hierachy['drugs'][drug_num]['drug_simple_generic_name']
                    pharmsubclass_num = dt_drug_hierachy['drugs'][drug_num]['pharmsubclass']
                    drug_pharmaceutical_subclass_name = dt_drug_hierachy['pharmsubclasses'][pharmsubclass_num]['name']
                    pharmclass_num = dt_drug_hierachy['pharmsubclasses'][pharmsubclass_num]['pharmclass']
                    drug_pharmaceutical_class_name = dt_drug_hierachy['pharmclasses'][pharmclass_num]['name']
                    # the end datetime of an order is the last admin datetime
                    end_datetime = admin_start_datetime
                    output_row = []
                    output_row.append(project_id)
                    output_row.append(start_datetime.strftime("%Y-%m-%d %H:%M"))
                    output_row.append(end_datetime.strftime("%Y-%m-%d %H:%M"))
                    output_row.append(MedicationOrderKey)
                    output_row.append("")
                    output_row.append(medication_order_id)
                    output_row.append("")
                    output_row.append(drug_code)
                    output_row.append(drug_name)
                    output_row.append("")
                    output_row.append(drug_simple_generic_name)
                    output_row.append("")
                    output_row.append(drug_pharmaceutical_class_name)
                    output_row.append(drug_pharmaceutical_subclass_name)
                    output_row.append(encounter_key)
                    writer.writerow(output_row)

        print()


    outfilepath = outfilepath.replace("medication_orders.csv", "medication_admins.csv")
    log_debug("Creating RDV: {0}".format(outfilepath))

    # project_id,medication_order_id,MedicationOrderKey,start_datetime,end_datetime,prn_dose,drug_code,drug_name,
    # admin_seq,intended_frequency,route_name,medication_order_mode_name,sched_admin_datetime

    with open(outfilepath, 'w', newline='') as ofile_handle:

        writer = csv.writer(ofile_handle)

        # output header
        output_row = []
        output_row.append("project_id")
        output_row.append("medication_order_id")
        output_row.append("MedicationOrderKey")
        output_row.append("start_datetime")
        output_row.append("end_datetime")
        output_row.append("prn_dose")
        output_row.append("drug_code")
        output_row.append("drug_name")
        output_row.append("admin_seq")
        output_row.append("intended_frequency")
        output_row.append("route_name")
        output_row.append("medication_order_mode_name")
        output_row.append("sched_admin_datetime")
        writer.writerow(output_row)

        medication_admin_num = 0

        for project_id in drug_administrations:

            for day_num in drug_administrations[project_id]:

                for drug_num in drug_administrations[project_id][day_num]:
                    sys.stdout.write("\r \rProcessing day: {0}, drug: {1}, Medication admins: {2} of {3}".format(day_num,
                                                                                                       drug_num,
                                                                                                       medication_admin_num,
                                                                                                       number_medication_admins))
                    sys.stdout.flush()

                    doses_per_day = drug_administrations[project_id][day_num][drug_num]['doses_per_day']
                    MedicationOrderKey = drug_administrations[project_id][day_num][drug_num]['MedicationOrderKey']
                    medication_order_id = drug_administrations[project_id][day_num][drug_num]['medication_order_id']
                    start_datetime = drug_administrations[project_id][day_num][drug_num]['start_datetime']
                    drug_code = dt_drug_hierachy['drugs'][drug_num]['drug_code']
                    drug_name = dt_drug_hierachy['drugs'][drug_num]['drug_name']

                    for admin_seq in range(1,doses_per_day + 1):

                        medication_admin_num += 1

                        if admin_seq == 1:
                            admin_datetime = start_datetime
                        else:
                            # first admin of the day will be 06:00 then 10:00, 14:00, 18:00, 22:00 - check not already discharged
                            if admin_seq == 2:
                                hours = 10
                            elif admin_seq == 3:
                                hours = 14
                            elif admin_seq == 4:
                                hours = 18
                            else:
                                hours = 22

                            admin_datetime = datetime.combine(start_datetime.date(), datetime.min.time()) + \
                                                   timedelta(minutes=int(10 * 60)) + timedelta(days=admin_day_num)

                        if admin_datetime >= start_datetime:

                            output_row = []
                            output_row.append(project_id)
                            output_row.append(medication_order_id)
                            output_row.append(MedicationOrderKey)
                            output_row.append(admin_datetime.strftime("%Y-%m-%d %H:%M"))
                            output_row.append(admin_datetime.strftime("%Y-%m-%d %H:%M"))
                            output_row.append("")
                            output_row.append(drug_code)
                            output_row.append(drug_name)
                            output_row.append(admin_seq)
                            output_row.append("")
                            output_row.append("")
                            output_row.append("")
                            output_row.append("sched_admin_datetime")
                            writer.writerow(output_row)

        print()

    log_debug("Function complete: {0}".format(inspect.currentframe().f_code.co_name))


def get_age_group(age_in_units, unit="day"):

    if unit == "year":
        age = age_in_units
    else:
        age = age_in_units/365

    if age < 3.0:
        age_group = "00to02"
    elif age < 6.0:
        age_group = "03to05"
    elif age < 12.0:
        age_group = "06to11"
    elif age < 18.0:
        age_group = "12to17"
    elif age < 21.0:
        age_group = "18to20"
    elif age < 26.0:
        age_group = "21to25"
    elif age < 50.0:
        age_group = "26to49"
    elif age < 70.0:
        age_group = "50to69"
    elif age < 80.0:
        age_group = "70to79"
    else:
        age_group = "80plus"

    return age_group


def get_ha_id(df_ha_rdv, project_id, start_datetime, end_datetime):

    ha_id = None

    df_selection = df_ha_rdv[['ha_id','start_datetime','end_datetime']].loc[df_ha_rdv['project_id'] == project_id]

    if len(df_selection.index) == 1:
        ha_id = df_selection.iloc[0, 0]
    else:
        for index, row in df_selection.iterrows():
            ha_id = row['ha_id']
            # check dates

    pause = True

    return ha_id


def create_rdv_dots(csv_project_path, sub_project):

    # Files created
    #
    # sp01_caboodle_patient_demographics.csv
    #project_id	hospital_no	birth_date	death_date	deceased_flag	sex	ethnicity_nat_code	ethnicity_local_code	ethnicity_name
    #
    # sp01_caboodle_patient_hospital_admissions.csv
    # project_id	encounter_key	patient_class	hospital_service	admission_type	admission_source	disharge_disposition	principal_problem	start_datetime	end_datetime
    #
    # sp01_caboodle_patient_medication_orders.csv
    # project_id	start_datetime	end_datetime	MedicationOrderKey	ordered_datetime	medication_order_id	sequence_number	drug_code	drug_name	drug_gpi	drug_simple_generic_name	drug_therapeutic_class_name	drug_pharmaceutical_class_name	drug_pharmaceutical_subclass_name	dose_amount	formulation_code	intended_frequency	quantity	dose	dose_range	calculated_dose_range	dose_number	route_name	indication	indication_comments	response	medication_order_name	medication_order_mode_name	medication_order_class_name	medication_order_source_name	disps_this_period	admins_this_period	first_admin_datetime	encounter_key
    #
    # sp01_caboodle_patient_medication_admins.csv
    # project_id	medication_order_id	MedicationOrderKey	start_datetime	end_datetime	prn_dose	drug_code	drug_name	admin_seq	intended_frequency	route_name	medication_order_mode_name	sched_admin_datetime
    #
    # sp01_caboodle_patient_medication_comeds.csv
    # sp01_caboodle_patient_medication_adminsinfo.csv

    # Demographics
    # patient - project id
    # Age  - create age groups as per patient_details
    # Sex - M, F, U
    #
    # Hospital Admissions
    # patient - project id
    #
    # Drug adminstrations
    # patient - project_id
    # Day
    # Drug
    # Route
    # Pharmeceutical class
    # Pharmeceutical sub-class

    # Create a single file with columns:
    # Could have more than one admission for the same patient
    # project_id, sex, age_at_admission,  date, day of admission, medicationOrderKey, drug_simple_generic_name, Pharmeceutical sub-class, Pharmeceutical class

    log_debug("Read RDVs")
    file_name = f"{sub_project}_caboodle_patient_demographics.csv"
    inpfilepath = os.path.join(csv_project_path, file_name)
    df_dm_rdv = pd.read_csv(inpfilepath)

    df_dm_rdv['birth_date'] = pd.to_datetime(df_dm_rdv['birth_date'], dayfirst=True)

    file_name = f"{sub_project}_caboodle_patient_hospital_admissions.csv"
    inpfilepath = os.path.join(csv_project_path, file_name)
    df_ha_rdv = pd.read_csv(inpfilepath)

    df_ha_rdv['start_datetime'] = pd.to_datetime(df_ha_rdv['start_datetime'], dayfirst=True)
    df_ha_rdv['end_datetime'] = pd.to_datetime(df_ha_rdv['end_datetime'], dayfirst=True)

    # Add in ha_id
    df_ha_rdv.insert(0, 'ha_id', range(1, 1 + len(df_ha_rdv)))

    file_name = f"{sub_project}_caboodle_patient_medication_orders.csv"
    inpfilepath = os.path.join(csv_project_path, file_name)
    df_mo_rdv = pd.read_csv(inpfilepath)

    df_mo_rdv['start_datetime'] = pd.to_datetime(df_mo_rdv['start_datetime'], dayfirst=True)
    df_mo_rdv['end_datetime'] = pd.to_datetime(df_mo_rdv['end_datetime'], dayfirst=True)

    # add in ha_id
    df_mo_rdv['ha_id'] = df_mo_rdv[['project_id', 'start_datetime', 'end_datetime']].apply(lambda row: get_ha_id(df_ha_rdv, row[0], row[1], row[2]), axis=1)

    file_name = f"{sub_project}_caboodle_patient_medication_admins.csv"
    inpfilepath = os.path.join(csv_project_path, file_name)
    df_ma_rdv = pd.read_csv(inpfilepath)

    # merge patients with hospital_admissions
    # merge on project_id
    df_dm_ha = pd.DataFrame.merge(df_dm_rdv[['project_id', 'birth_date', 'sex']], df_ha_rdv[['project_id', 'ha_id', 'start_datetime', 'end_datetime']], on=['project_id'], how='inner', suffixes=("_dm", "_ha"))

    log_debug("Demographics merged with Hospital admissions: {0}".format(len(df_dm_ha.index)))

    # Add in age at admission
    log_debug("Calculate age at admission")
    df_dm_ha['age_at_admission'] = df_dm_ha['start_datetime'] - df_dm_ha['birth_date']
    df_dm_ha['age_at_admission'] = df_dm_ha['age_at_admission'].apply(lambda x: int(x.total_seconds()/(24*60*60)))
    df_dm_ha['age_group_at_admission'] = df_dm_ha['age_at_admission'].apply(lambda x: get_age_group(x))

    # merge on project_id and encounterKey
    df_dm_ha_mo = pd.DataFrame.merge(df_dm_ha, df_mo_rdv[['project_id', 'ha_id', 'MedicationOrderKey', 'drug_simple_generic_name', 'drug_pharmaceutical_class_name', 'drug_pharmaceutical_subclass_name']],
                                     on=['project_id', 'ha_id'],
                                     how='inner',
                                     suffixes=("_dm_ha", "_mo"))

    log_debug("Merged with Medication Orders: {0}".format(len(df_dm_ha_mo.index)))

    # merge on project_id and encounterKey
    df_dm_ha_mo_ma = pd.DataFrame.merge(df_dm_ha_mo, df_ma_rdv[['project_id', 'MedicationOrderKey', 'start_datetime']], on=['project_id', 'MedicationOrderKey'], how='inner',
                                  suffixes=("_dm_ha_mo", "_ma"))

    log_debug("Calculate day of admission")
    df_dm_ha_mo_ma['start_datetime_ma'] = pd.to_datetime(df_dm_ha_mo_ma['start_datetime_ma'], dayfirst=True)
    df_dm_ha_mo_ma['day_of_admission'] = df_dm_ha_mo_ma['start_datetime_ma'] - df_dm_ha_mo_ma['start_datetime_dm_ha_mo']
    df_dm_ha_mo_ma['day_of_admission'] = df_dm_ha_mo_ma['day_of_admission'].apply(lambda x: int(x.total_seconds()/(24*60*60)))

    log_debug("Merged with Medication Admins: {0}".format(len(df_dm_ha_mo_ma.index)))

    # drop un-required columns and remove duplicates
    df_dm_ha_mo_ma.drop(['birth_date', 'ha_id', 'age_at_admission', 'MedicationOrderKey', 'start_datetime_dm_ha_mo','end_datetime','start_datetime_ma'], axis=1, inplace=True)
    df_dm_ha_mo_ma.drop_duplicates(inplace=True)
    log_debug("Dropped duplicates: {0}".format(len(df_dm_ha_mo_ma.index)))

    file_name = f"{sub_project}_caboodle_patient_dots.csv"
    df_dm_ha_mo_ma.to_csv(os.path.join(csv_project_path, file_name), encoding='utf-8', index=False)

    log_debug("Complete")


def check_rdvs(dex_project_path, csv_project_path, sub_project=None, create_all=False):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    file_name_prefix = "" if sub_project is None else f"{sub_project}_"

    #########################################
    # RDVs - check all RDVs due to dependency
    #########################################

    rdvs = []
    rdvs.append(("demographics", "caboodle"))
    rdvs.append(("hospital_admissions", "caboodle"))
    rdvs.append(("medication_orders", "caboodle"))
    rdvs.append(("dots", "caboodle"))

    patient_list_file_name = f"{file_name_prefix}patient_list.csv"
    plist_filepath = os.path.join(dex_project_path, patient_list_file_name)

    for rdv, source in rdvs:

        file_name = f"{file_name_prefix}{source}_patient_{rdv}.csv"
        inpfilepath = os.path.join(csv_project_path, file_name)

        # load RDV into dataframe and pass to relevant function
        log_debug("Processing RDV: {0}, file: {1}".format(rdv, file_name))

        if rdv == "demographics":
            demographics_filepath = inpfilepath
            if not os.path.exists(inpfilepath) or not os.path.exists(plist_filepath) or create_all:

                if sub_project == "sp01":
                    number_patients = 10
                elif sub_project == "sp02":
                    number_patients = 100
                else:
                    number_patients = 250

                birth_date_start_date = date(2010, 1, 1)
                birth_date_end_date = date(2021, 5, 31)
                death_percentage = 0.0

                create_rdv_demographics(inpfilepath, plist_filepath, number_patients, birth_date_start_date, birth_date_end_date, death_percentage)

                create_all = True

        elif rdv == "hospital_admissions":
            hospital_admissions_filepath = inpfilepath
            if not os.path.exists(inpfilepath) or create_all:

                ha_start_date = date(2019, 5, 1)
                ha_end_date = date(2021, 5, 31)
                ha_min_stay = 7
                ha_max_stay = 14

                create_rdv_hospital_admissions(inpfilepath, demographics_filepath, plist_filepath, ha_start_date, ha_end_date, ha_min_stay, ha_max_stay)

                create_all = True

        elif rdv == "medication_orders":
            medication_orders_filepath = inpfilepath
            if not os.path.exists(inpfilepath) or create_all:
                

                if sub_project == "sp01":
                    number_drugs = 50
                    number_pharmsubclass = 10
                    number_pharmclass = 5
                elif sub_project == "sp02":
                    number_drugs = 100
                    number_pharmsubclass = 25
                    number_pharmclass = 10
                else:
                    number_drugs = 150
                    number_pharmsubclass = 35
                    number_pharmclass = 15

                max_doses_per_day = 3  # max is 5
                min_admin_days = 1
                max_admin_days = 3

                dt_drug_hierachy = create_dt_drug_hierachy(number_drugs, number_pharmsubclass, number_pharmclass,
                                                           max_doses_per_day, min_admin_days, max_admin_days)

                max_orders_per_day = 12

                create_rdv_medication_orders(inpfilepath, hospital_admissions_filepath, dt_drug_hierachy, max_orders_per_day)

                create_all = True

        elif rdv == "dots":
            if not os.path.exists(inpfilepath) or create_all:
                create_rdv_dots(csv_project_path, sub_project)

                create_all = True


def plot_barchart(fig, row, col, df_rdv, column_name, count_column='project_id', stack_column=None,
                  x_axis_title=None, y_axis_title='Patients', groupby=True, x_axis=None, colors=None):

    # group by
    # Create a unique list of patients
    log_debug(f"Get list of categories in column {column_name}")

    if x_axis_title is None:
        if stack_column is None:
            x_axis_title = column_name
        else:
            x_axis_title = f"{column_name} by {stack_column}"

    if colors is None:
        colors = "#a3a6e6" # light blue

    if stack_column is None:
        if groupby:

            unique_columns = [column_name]
            df_groupby = df_rdv.groupby(
                unique_columns
            ).agg(
                {
                    count_column: 'count'
                }
            )

            df_groupby[column_name] = df_groupby.index

            prov_x_axis = df_groupby[column_name].tolist()
            prov_y_axis = df_groupby[count_column].tolist()

        else:

            prov_x_axis = df_rdv[column_name].tolist()
            prov_y_axis = df_rdv[count_column].tolist()

        if x_axis is not None:
            y_axis = []
            for x_tick in x_axis:
                for tick_num, prov_x_tick in enumerate(prov_x_axis):
                    y_axis.append(0)
                    if x_tick == prov_x_tick:
                        y_axis[tick_num] = prov_y_axis[tick_num]
                        break

            fig.add_trace(go.Bar(x=x_axis, y=y_axis, marker_color=colors, text=y_axis, textposition='auto'), row=row, col=col)

        else:
            fig.add_trace(go.Bar(x=prov_x_axis, y=prov_y_axis, marker_color=colors, text=prov_y_axis, textposition='auto'), row=row, col=col)

    else:

        # get list of stacked categories:
        unique_columns = [stack_column]
        df_groupby = df_rdv.groupby(
            unique_columns
        ).agg(
            {
                count_column: 'count'
            }
        )

        df_groupby[column_name] = df_groupby.index

        stack_categories = df_groupby[column_name].tolist()

        for stack_num, stack_category in enumerate(stack_categories):
            include = df_rdv[stack_column] == stack_category
            df_filter = df_rdv[include]

            if groupby:

                unique_columns = [column_name]
                df_groupby = df_filter.groupby(
                    unique_columns
                ).agg(
                    {
                        count_column: 'count'
                    }
                )

                df_groupby[column_name] = df_groupby.index

                x_axis = df_groupby[column_name].tolist()
                y_axis = df_groupby[count_column].tolist()

            else:

                x_axis = df_filter[column_name].tolist()
                y_axis = df_filter[count_column].tolist()

            stack_color = colors[stack_num]
            fig.add_trace(go.Bar(name=stack_category, x=x_axis, y=y_axis, marker_color=stack_color, text=y_axis, textposition='auto'), row=row, col=col)

            fig.update_layout({"barmode": "stack"})

    fig.update_xaxes(title_text=x_axis_title, title_font_size=20, tickfont_size=16, row=row, col=col)
    fig.update_yaxes(title_text=y_axis_title, title_font_size=20, tickfont_size=16, row=row, col=col)

    return fig


def create_rdv_visualisation(rdvs, project, dex_project_path, csv_project_path, sub_project=None, phase=None, stage=1):

    called_by = inspect.currentframe().f_back.f_back.f_code.co_name \
        if inspect.currentframe().f_back.f_code.co_name == "wrapper" \
        else inspect.currentframe().f_back.f_code.co_name

    log_debug("Running function: {0}, Called by: {1}".format(inspect.currentframe().f_code.co_name, called_by))

    file_name_prefix = "" if sub_project is None else f"{sub_project}_"

    ######
    # RDVs
    ######

    fig = make_subplots(rows=2, cols=2)

    for rdv, source in rdvs:

        file_name = f"{file_name_prefix}{source}_patient_{rdv}.csv"
        inpfilepath = os.path.join(csv_project_path, file_name)

        # load RDV into dataframe and pass to relevant function
        log_debug("Processing RDV: {0}, file: {1}".format(rdv, file_name))
        df_rdv = pd.read_csv(inpfilepath)

        if rdv == "demographics":
            # plot sex
            column_name = "sex"
            colorscale = ["#fde725", "#90d743"]
            fig = plot_barchart(fig, row=1, col=1, df_rdv=df_rdv, column_name=column_name, colors=colorscale)

        if rdv == "hospital_admissions":
            log_debug("Calculate length of stay")
            df_rdv['start_datetime'] = pd.to_datetime(df_rdv['start_datetime'], dayfirst=True)
            df_rdv['end_datetime'] = pd.to_datetime(df_rdv['end_datetime'], dayfirst=True)
            df_rdv['length_of_stay'] = df_rdv['end_datetime'] - df_rdv['start_datetime']
            df_rdv['length_of_stay'] = df_rdv['length_of_stay'].apply(lambda x: int(round(x.total_seconds() / (60*60*24),0)))
            # plot length of stay
            column_name = "length_of_stay"
            df_length_of_stay = df_rdv[['project_id', column_name]].drop_duplicates()

            # fig = plot_barchart(fig, row=2, col=1, df_rdv=df_length_of_stay, column_name=column_name)

        elif rdv == "dots":
            # plot age_group_at_admission
            column_name = "age_group_at_admission"
            df_age_group = df_rdv[['project_id', column_name]].drop_duplicates()

            # list of "N" colors between "start_color" and "end_color"
            # start_color = "#ff0000"  # red
            # end_color = "#ee82ee"  # violet
            start_color = "#35b779"  # viridis
            end_color = "#440154"  # viridis

            N = len(age_groups)
            colorscale = [x.hex for x in list(Color(start_color).range_to(Color(end_color), N))]
            age_colorscale = colorscale
            fig = plot_barchart(fig, row=1, col=2, df_rdv=df_age_group, column_name=column_name, x_axis=age_groups, colors=colorscale)

            # Now want to merge length_of_stay and age_group_at_admission
            df_merge = df_length_of_stay.merge(df_age_group, on="project_id")

            column_name = "length_of_stay"
            stack_column = "age_group_at_admission"
            fig = plot_barchart(fig, row=2, col=1, df_rdv=df_merge, column_name=column_name, stack_column=stack_column, colors=age_colorscale)

            pause = True

            # get number of patients per day
            column_name = "day_of_admission"
            df_unqiue = df_rdv[['project_id', column_name]].drop_duplicates()

            # plot adminsitrations per data - unique drug each day - row level of DOTs
            count_column = 'drug_simple_generic_name'

            # Get Number of patients per day of admission
            unique_columns = [column_name]
            df_daily_patients = df_unqiue.groupby(
                unique_columns
            ).agg({'project_id': 'count'})

            # Get number of drug administrations per day of admission
            unique_columns = [column_name]
            df_daily_drugs = df_rdv.groupby(
                unique_columns
            ).agg({ count_column: 'count' })

            # Merge dataframes and create average
            df_merge = df_daily_drugs.merge(df_daily_patients, left_index=True, right_index=True)
            df_merge[column_name] = df_merge.index
            df_merge['drug_administrations_per_patient'] = df_merge[count_column] / df_merge['project_id']
            df_merge['drug_administrations_per_patient'] = df_merge['drug_administrations_per_patient'].apply(lambda x: int(round(x,0)))

            fig = plot_barchart(fig, row=2, col=2, df_rdv=df_merge, column_name=column_name, count_column='drug_administrations_per_patient',
                                  y_axis_title='Drug Administrations per patient', groupby=False)

    fig.update_layout(showlegend=False,
                      title_text=f"Cohort Visualisation, sub project: {sub_project}", title_font_size=20)

    inFilePath = os.path.join(dex_project_path, f"{sub_project}_{phase}_{stage}_analytics_summary.html")
    fig.write_html(inFilePath, auto_open=True)


def main():

    '''
    '''

    log_debug("Started!")

    # Ignore python script name - check project paths
    dex_project_path, csv_project_path, gml_project_path = check_project_path(sys.argv[1:],
                                                                project_path = "Z:\\Projects\\Research\\0200-GRACE")

    if dex_project_path is not None:

        phase = "check_rdvs"

        run_stages = get_stages(sys.argv[1:], default=[1, 2, 3 ])

        log_debug(f"Phase: {phase}, stages: {run_stages}")

        # Stage 1 - sp01 - 10 patients
        # Stage 2 - sp02 - 100 patients
        # stage 3 - sp03 - all patients (252)

        for stage in run_stages:

            if stage in [1, ]:
                sub_project = "sp01"
            elif stage in [2, ]:
                sub_project = "sp02"
            else:
                sub_project = "sp03"

            rdvs = []
            rdvs.append(("demographics", "caboodle"))
            rdvs.append(("hospital_admissions", "caboodle"))
            rdvs.append(("medication_orders", "caboodle"))
            rdvs.append(("dots", "caboodle"))

            check_rdvs(dex_project_path, csv_project_path, sub_project)

            create_rdv_visualisation(rdvs, project, dex_project_path, csv_project_path, sub_project=sub_project, phase=phase,
                                     stage=stage)

    log_debug("Done!")

if __name__ == "__main__":
    main()
