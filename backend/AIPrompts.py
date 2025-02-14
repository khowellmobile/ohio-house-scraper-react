""" The following is a biography of a member of the Ohio State House of Representatives. Based on the biography, return a summarization following these instructions:

        Summarization Format:
            1. Education
                a. List educational background in the format: University, Degree, Area of Study.
                b. If any of the three sections are missing, omit that section and any commas. For example:
                    b1. "The Ohio State University, MS, Political Science"
                    b2. "Ohio University, BS, Nursing"

            2. Political Experience
                a. List political experience in the format: Organization, Role, Term.
                b. Include terms from any Ohio House or Senate, U.S. House or Senate, or City Council.
                c. If any section is missing, omit it and do not add extra commas. For example:
                    c1. "House of Representatives, Majority Whip, 2017-2021"
                    c2. "Columbus City Council, President"

            3.Employment History
                a. List past employment in the format: Organization, Role, Status.
                b. Include any business ventures like buying or starting companies.
                c. If any section is missing, omit it and do not add extra commas. For example:
                    c1. "JP Morgan Chase, Accountant, Formerly"
                    c2. "Bought Johns Company"
                    c3. "Started Columbus Mowing"

            Community Involvement
                a. List community involvement in the format: Organization, Role.
                b. This includes churches, local organizations, school boards, etc.
                c. If only the organization is available, list it alone. For example:
                    c1."Church of God"
                    c2."Neighborhood Watch, Captain"

        Output Instructions:
            1. The output should be a single line, with sections (education, political experience, employment, community involvement) separated by a pipe (|).
            2. If any section has no data, leave it empty (i.e., '||').
            3. If no biography is provided, return "||||".
            4. Ensure there are no extra commas or new line breaks. 
            
        Biography:
        """

    
"""

    The text at the end of this prompt is a biography for a memeber Ohio State House of Representatives. Using the biography return a summarization of the biography. The summarization format and notes on each section is described next.

    Summarization format and information:

    1. A comma delimited list of their education.
        a. The list should follow the format 'University, Degree, Area of Study'.
        b. If one of the three sections is not specified then leave it blank. In this case do not include the comma either. This means the list could be "University, Degree", "Degree, Area of Study", Etc.
        c. Here is an example of what a representatives list might look like "The Ohio State University, MS, Political Science, Ohio University, BS, Nursing"
    2. A comma delimited list of their past political experience. 
        a. The list should follow the format 'Organization, Role, Term'
        b. If one of the three sections is not specified then leave it blank. In this case do not include the comma either. This means the list could be "Organization, Term", "Role, Term", Etc.
        c. The political experience can include Previous Terms in the house or senate of anywhere and city councils.
        d. Here is an example of what a representatives list might look like "House of Representatives, Majority Whip, 2017-2021, Columbus City Council, Gahanna City Council, President"
        e. Only occurences of terms in a city council, ohio house of representatives, ohio senate, united states house of representatives, united states senate are classified as political experience
    3. A comma delmited list of their employment history.
        a. The list should follow the format 'Organization, Role, Status'.
        b. If any section is missing, omit it entirely. Do not include extra commas for missing sections This means the list could be "Organization, Status", "Role, Status", Etc.
        c. Include any instances of buying, selling, or starting businesses
        d. Here is an example of what a representatives list might look like "JP Morgan Chase, Accountant, Formerly, Bought Johns Company, Started Columbus Mowing"
    4. A comma delimited list of their community involvement. This includes churches, local organizations, school boards, etc.
        a. The list should follow the format 'Organization, role'.
        b. It is possible that only an organization is listed. If so then include the organziation. E.g. "Church of God"
        c. Here is an example of what a representatives list might look like "Member of General Church, Neighborhood Watch, Captain"

    Listed next in any general instructions for generating the lists and the total output.

    1. The total output should be a list delimited by "|". Where each section (education, politcal history, employment history, community involvement) makes up an element in the list
    2. Pieces of information should only go into one category and should not appear in multiple categories. Eg. A member of the neighbor hood watch only classifies as community involvement and NOT employment.
    3. If a biography does not mention a section then do not include it. In this case still delimit the section. E.g. if a rep does not have employement history "Education list|Political history list||Community involvement list" would be the format of the output
    4. If no text for the bio is provided then return "||||"
    5. No new line operators or instances of the string ", ," should exist in the response 

    Biography:
    """

        
