""" 
Notes on below prompt prompt: Used until 2/21/2025. AI Has a hard time sorting items into the proper buckets. Repeats of political and education are an issue. If bio only
provides education experience AI will separate out the degrees into multiple buckets.

The following is a biography of a member of the Ohio State House of Representatives. Based on the biography, return a summarization following these instructions:

        Summarization Format:
            1. Education
                a. List educational background in the format: University, Degree, Area of Study.
                b. If any of the three sections are missing, omit that section and any commas. For example:
                    b1. "The Ohio State University, MS, Political Science"
                    b2. "Ohio University, BS, Nursing"

            2. Political Experience
                a. List political experience in the format: Organization, Role, Term.
                b. Include terms from any Ohio House or Senate, U.S. House or Senate, or City Council.
                c. If the term years are not specifically enumerated then do not include them
                d. If any section is missing, omit it and do not add extra commas. For example:
                    d1. "House of Representatives, Majority Whip, 2017-2021"
                    d2. "Columbus City Council, President"

            3.Employment History
                a. List past employment in the format: Organization, Role, Status.
                b. Include any business ventures like buying or starting companies.
                c. If any section is missing, omit it and do not add extra commas. For example:
                    c1. "JP Morgan Chase, Accountant, Formerly"
                    c2. "Bought Johns Company"
                    c3. "Started Columbus Mowing"

            4. Community Involvement
                a. List community involvement in the format: Organization, Role.
                b. This includes churches, local organizations, school boards, etc.
                c. If only the organization is available, list it alone. For example:
                    c1."Church of God"
                    c2."Neighborhood Watch, Captain"

        General Instructions for Summarization:
            1. Segments of information (jobs, terms in office, organizations) are only put in the category they most belong in.
                a. Examples include
                    a1. A term in the Ohio House should only be put into Political Experience and should not also be put into into community involvement.
                    a2. A degree should not be listed in Community Involvement, Employment History, and Education. It should only be listed in Education.
            2. Terms in the Ohio House or Senate, U.S. House or Senate, or City Council should only be listed under Political Experience
            3. Attending a college or university and any mention of a degree should only be listed under education.
            4. Multiple degrees are all put in the same bucket seperated by commas.
                a. E.g. "The Ohio State University, MS, Nursing, Toledo University, BS, Biology|||"
        
        Examples of summarizations to use for comparison:


        Output Instructions:
            1. The output should be a single line, with sections (education, political experience, employment, community involvement) separated by a pipe (|).
                a1. e.g. 'education | political experience | employment | community involvement'.
            2. If any section has no data, leave it empty (i.e., '||').
            3. If no biography is provided, return "||||".
            4. Ensure there are no extra commas or new line breaks. 
            5. Ensure the output does not have any newline operators. ie "\n, \r, \u2028, \u2029" 
            6. Each output should contain exactly 3 pipe characters (|).
            
        Biography:
        """


""" 
Notes on this prompt: Started using 2/21/2025 in an attempt to fix issue with sorting of information. Tried to make it more clear in language by using term "Bucket" and using language
that shows that not every bucket needs to be filled. Did not fix issue with bucket sorting. Also had issue with term years. 


Based upon the biography provided, you are to pull relevant information and put it into one of 4 buckets. Each bucket will correspond to a kind of information
    that may or may not be in the biography. Buckets are listed below

        Summarization Format:
            Bucket 1. Education
                a. List educational background in the format: University, Degree, Area of Study.
                b. If any of the three sections are missing, omit that section and any commas. For example:
                    b1. "The Ohio State University, MS, Political Science"
                    b2. "Ohio University, BS, Nursing"

            Bucket 2. Political Experience
                a. List political experience in the format: Organization, Role, Term.
                b. Include terms from any Ohio House or Senate, U.S. House or Senate, or City Council.
                c. If any of the three sections are missing, omit that section and any commas. For example:
                    c1. "House of Representatives, Majority Whip, 2017-2021"
                    c2. "Columbus City Council, President"

            Bucket 3. Employment History
                a. List past employment in the format: Organization, Role, Status.
                b. Include any business ventures like buying or starting companies.
                c. If any of the three sections are missing, omit that section and any commas. For example:
                    c1. "JP Morgan Chase, Accountant, Formerly"
                    c2. "Bought Johns Company"
                    c3. "Started Columbus Mowing"

            Bucket 4. Community Involvement
                a. List community involvement in the format: Organization, Role.
                b. This includes churches, local organizations, school boards, etc.
                c. If only the organization is available, list it alone. For example:
                    c1."Church of God"
                    c2."Neighborhood Watch, Captain"

        General Instructions for Summarization:
            1. Segments of information (jobs, terms in office, organizations) are only put in the category they most belong in.
            2. Each segment of information should only appear once in the output.
                a. An example is
                    a1. A term in the Ohio House should only be put into Political Experience and should not also be put into into community involvement.
                    a2. Attending a college or university and any mention of a degree should only be listed under education.
            3 A bucket can hold multiple segments of information. Every segment and sub segment (organization, role, status, etc.) should be comma delimited

        Output Instructions:
            1. Each bucket of information (education, political experience, employment, community involvement) is seperated by a pipe (|).
                a1. e.g. 'education | political experience | employment | community involvement'.
            2. If any section has no data, leave it empty (i.e., '||'). If no biography is provided, return "|||".
            3. Ensure the output does not have any newline operators. ie "\n, \r, \u2028, \u2029", no extra commas, and no extra line breaks
            4. Each output should have exactly 3 pipes. 
            
        Biography:
        """

"""
Bio Prompt 3: Seems to have best performance so far. Corrected for it wanting to add human speech before result.
Efficacy on political experience is still not as high as wanted. Will also fill empty buckets with the name of the bucket sometimes.
Really does NOT like "thaddeus-j-claggett" for some reason. This iteration will error loop on him everytime still working on identifying why

Included at the end of this prompt is a biography. The biography should be broken into segments of information (check section 1. to see examples of a segment of information).
Once the biography is broken down into segments these segments should be sorted into 1 of 5 buckets (check section 2. for information on buckets and sorting). Once the 
information is sorted into the appropriate buckets the output needs to be summarized, formatted, and returned.

Section 1. (Segments of information)
    Defintion of a segment of information: A segment of information is a collection of words that describe a membership/participation to 
        an organization, job, degree, or term in office.
    Examples of segments of information include:
        a. His educational background includes a BA, in Urban Studies
        b. He received a Master of Legal Studies from Cleveland State University School of Law
        c. Kyle has served on the Executive Committee of several Civic and Community Organizations including the Cleveland Chapter of the NAACP
        d. National Association of Community Health Workers
        e. Rep. Dane served as an award-winning public school teacher for three decades
        f. as well as a Parma councilman for nearly two decades
        g. Rep. Smith joined the Ohio House of Representatives in 2023 and is now serving his second term
        h. State Representative John Doe is serving his second term in the Ohio House of Representatives.

Section 2. (Buckets and sorting)
    Definition of a bucket: A collection of segments of information that are related by a topic
    Buckets:
        1. Education: This bucket includes any segments of information pertaining to a degree.
            1a. Examples include
                a. His educational background includes a BA, in Urban Studies
                b. He received a Master of Legal Studies from Cleveland State University School of Law
                c. She holds a degree in Social Work from Indiana University
                d. They earned a Masters degree from MIT
            1b. Look for keywords such as degree, university, Masters, Bachelors, PhD, Studied
        2. Political Experience: This bucket includes any segments of information pertaining to a term in office for Senate, House, or City Council
            2a. Examples include
                a. Rep. Smith joined the Ohio House of Representatives in 2023 and is now serving his second term
                b. State Representative John Doe is serving his second term in the Ohio House of Representatives.
                c. During his previous service in the House, his peers elected him Majority Whip and he chaired two standing committees. 
            2b. Look for keywords such as term, council, house of representatives, sentate, city council, elected
            2c. ONLY terms on a city countil, senate, or house of representatives are included here. Awards and Commitees are not sorted into this bucket.
        3. Employment History: This bucket includes any segments of information pertaining to employment and starting/selling/buying companies
            3a. Examples include
                a. He went on to serve as Southwest Ohio Outreach Director for For Ohios Future Action Fund
                b. The family works together to operate SFIA Enterprises
                c. Badger Run Berries, Sarahs company
            3b. Look for keywords such as works, bought, sold, company, worked, employed
        4. Commmunity Involvement: This bucket contains segments of information pertaining to communities, volunteering, churches, and extracurricular organizations
            4a. Examples include
                a. Belongs to St. Pauls Church
                b. The Does are parishioners of Sts. Constantine and Helen Greek Orthodox Church
                c. Patrols her neighborhood as a member of the neighborhood watch
            4b. Look for keywords such as belongs to and helps with, volunteers
        5. Other: This bucket contains segments of information that do not fall into one of the previous 4 buckets.
            5a. Examples unclude
                a. Claggett has been married to his wife for more than 27 years and they reside in Newark where they raised two children.
                b. and is currently in the process of writing his Masters theses. 
                c. He worked to expand school choice and empower parents to be active participants in their childs education regardless of income or circumstance.
            5b. This bucket may also include segments of information that describe another segment. Such as what they wanted to do or goals they had while serving a term
                or participating in an organization
    Sorting:
        1. Each segment of information should get sorted into a single bucket. A segment of information should not be placed into two buckets.
        2. If you feel a segment could belong in two buckets put it in the bucket it most belongs to.
        3. Not all buckets will be full as the bio may not have information that would sort into a bucket

Section 3. (formatting and summarization)
    Once all segments are sorted into buckets each segment should be summarized into a certain format. There is a summarization format that corresponds to each bucket.
    The formats are as listed below
    1. Education
        Format: University, Degree, Area of Study
        If a section of the format is not listed then omit that section and any commas.
        Examples of segment summarization:
            a. The Ohio State University, MS, Political Science
            b. Ohio University, BS, Nursing
            c. Ohio Unviersity, BS
            d. The Ohio State University, Political Science
        Example of entire bucket:
            a. Kent State University, BS, Visual Journalism, United States Naval War College, Command and Staff Program, University of Toledo, MS
    2. Political Experience
        Format: Organization, Role, Term
        If a section of the format is not listed then omit that section and any commas.
        Examples of segment summarization:
            a. Ohio House of Representatives, Majority Whip
            b. Ohio House of Representatives, Speaker, 2017-2020
            c. Ohio Senate, 2015-Preset
            d. Columbus City Council
        Example of entire bucket once summarized:
            a. Ohio House of Representatives, Speaker, 2017-2020, Ohio Senate, 2015-2017, Columbus City Council
    3. Employment
        Format: Organization, Role, Status
        If a section of the format is not listed then omit that section and any commas.
        If a company was bought/sold/started the summarization should be "Action, Company Name"
        Examples of segment summarization:
            a. McDonalds, Manager, Former
            b. Chase Bank, Analyst
            c. Started Scotts Mowing
            d. B&H Cleaning, CEO, Current
        Example of entire bucket:
            a. B&H Cleaning, CEO, Current, Started Scotts Mowing, Chase Bank, Analyst
    4. Community Involvement
        Format: Organization, Role
        If a section of the format is not listed then omit that section and any commas.
        Examples of segment summarization:
            a. St. Pauls Church, Pastor
            b. Neighborhood Watch
            c. Columbus for Hunger, Member
            d. Soup Kitchen
        Example of entire bucket:
            a. St. Pauls Church, Pastor, Neighborhood Watch, Columbus for Hunger, Member, Soup Kitchen
    5. Other
        Segments of information in this bucket do not need formatting

Section 4. (Final Ouput)
    Notes about output: 
        1. Bucket 5 should be left out of the final output and not considered beyond this point
        2. Create a list of buckets 1 through 4 delimited by a pipe (|). 
        3. Buckets are ordered "Education | Political Experience | Employment | Community Involvement"
        3. If a bucket is empty still delimit it eg. ("||")
        4. Each output should have exactly 3 pipes regardless of if buckets are empty or not. eg ("|||")
        5. Here is an example of what a final output might look like
            "Kent State University, BS, Visual Journalism, University of Toledo, MS|Ohio Senate, 2015-2017, Columbus City Council|Started Scotts Mowing, Chase Bank, Analyst|St. Pauls Church, Pastor"
        6. Ensure there are no extra commas or new line breaks. 
        7. Ensure the output does not have any newline operators. ie "\n, \r, \u2028, \u2029"
        IMPORTANT 8. Return ONLY the pipe delimited list. Do NOT add any thing to the response. 
            8a. Example of incorrect response by adding something to the list would be "Here is the list as requested: |||"
            8b. Example of incorrect response would be "Here's a breakdown of the biography into segments, sorted into buckets, summarized, and formatted according to your specifications: |||"
            8c. Example of a correct response "Kent State University|||St. Pauls Church"

Section 5. (Biography)
    Biography:"""

        
