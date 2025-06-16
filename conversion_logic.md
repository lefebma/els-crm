Lead Conversion to Account, Contact, and Opportunity

Triggered when:

    • A lead is moved to the SQL stage (Sales Qualified Lead) - which displays a 'Convert' button.
    • The user clicks the “Convert to Account/Opp” button



🧠 
Conversion Logic Steps

    1. Check if lead is already converted
        ○ If lead.isConverted is true, exit function.
    2. Create an Account
        ○ Generate a new unique ID for the account.
        ○ Populate the account using lead.companyName and lead.notes.
        ○ Set createDate to the current date.
        ○ Add the new account to the accounts list.
    3. Create a Contact
        ○ Split lead.contactPerson into firstName and lastName.
        ○ Use lead.email for contact email.
        ○ Link the contact to the new account using accountId.
        ○ Set createDate and lastContact to today.
        ○ Add the new contact to the contacts list.
    4. Create an Opportunity
        ○ Generate a unique ID for the opportunity.
        ○ Use a name like Opportunity for {companyName}.
        ○ Set salesStage to "Prospecting", forecast to "0%".
        ○ Link it to the new account and contact using accountId and contactId.
        ○ Include initial nextSteps and requirements from the lead.
        ○ Add the opportunity to the opportunities list.
    5. Mark Lead as Converted
        ○ Update the lead’s isConverted flag to true.
    6. Navigate to the Opportunities Tab
        ○ Set activeTab to 'opportunities' to display the newly created opportunity.
