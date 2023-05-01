Feature: The promotion service back-end
    As a Marketing Manager
    I need a RESTful catalog service
    So that I can keep track of all the promotions

Background:
    Given the following promotions
        | name       | category           | available | promotype        |
        | christmas  | holiday            | False     | BUYONEGETONEFREE |
        | BFFs       | friends_and_family | True      | GET20PERCENTOFF  |
        | summer2023 | seasonal           | True      | UNKNOWN          |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotions!" in the title
    And I should not see "404 Not Found"


Scenario: Create and Read a Promotion
    When I visit the "Home Page"
    And I set the "Name" to "CyberMonday"
    And I set the "Category" to "Event"
    And I select "True" in the "Available" dropdown
    And I select "Get 20% off" in the "Promotype" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "CyberMonday" in the "Name" field
    And I should see "Event" in the "Category" field
    And I should see "True" in the "Available" dropdown
    And I should see "Get 20% off" in the "Promotype" dropdown

Scenario: List all promotions
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "BFFs" in the results
    And I should see "summer2023" in the results
    And I should not see "christmas" in the results

Scenario: Query for name
    When I visit the "Home Page"
    And I set the "Name" to "christmas"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "christmas" in the results
    And I should not see "summer2023" in the results
    And I should not see "BFFs" in the results

Scenario: Query for seasonal
    When I visit the "Home Page"
    And I set the "Category" to "seasonal"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "summer2023" in the results
    And I should not see "christmas" in the results
    And I should not see "BFFs" in the results

Scenario: Query for available
    When I visit the "Home Page"
    And I select "True" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "BFFs" in the results
    And I should see "summer2023" in the results
    And I should not see "christmas" in the results

Scenario: Delete a Promotion
    When I visit the "Home Page"
    And I set the "Name" to "christmas"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "christmas" in the "Name" field
    And I should see "holiday" in the "Category" field
    When I press the "Delete" button
    Then I should see the message "Promotion has been Deleted!"
    When I set the "Name" to "christmas"
    And I press the "Search" button
    Then I should see the message "Success"
    Then I should not see "christmas" in the results

Scenario: Activate a Promotion
    When I visit the "Home Page"
    And I set the "Name" to "CyberMonday"
    And I set the "Category" to "Event"
    And I select "False" in the "Available" dropdown
    And I select "Get 20% off" in the "Promotype" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Activate" button
    Then I should see the message "Success"
    And I should see "CyberMonday" in the "Name" field
    And I should see "True" in the "Available" dropdown

Scenario: Activate a Promotion
    When I visit the "Home Page"
    And I set the "Name" to "CyberMonday"
    And I set the "Category" to "Event"
    And I select "True" in the "Available" dropdown
    And I select "Get 20% off" in the "Promotype" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Deactivate" button
    Then I should see the message "Success"
    And I should see "CyberMonday" in the "Name" field
    And I should see "False" in the "Available" dropdown

Scenario: Update a promotion category
    When I visit the "Home Page"
    And I set the "Name" to "christmas"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "holiday" in the "Category" field
    When I set the "Category" to "seasonal"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "christmas" in the "Name" field
    And I should see "seasonal" in the "Category" field
    And I should not see "holiday" in the "Category" field
    And I should see "false" in the "Available" dropdown
    And I should see "Get 20% off" in the "Promotype" dropdown

Scenario: Update a promotion name
    When I visit the "Home Page"
    And I set the "Name" to "christmas"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "seasonal" in the "Category" field
    When I set the "Name" to "winterholiday"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "winterholiday" in the "Name" field
    And I should not see "christmas" in the "Name" field
    And I should see "seasonal" in the "Category" field
    And I should see "false" in the "Available" dropdown
    And I should see "Get 20% off" in the "Promotype" dropdown

Scenario: Update a promotion type
    When I visit the "Home Page"
    And I set the "Name" to "christmas"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Buy one, get one free" in the "Promotype" dropdown
    When I set the "Promotype" to "Get 20% Off"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    And the "Promotype" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "christmas" in the "Name" field
    And I should see "seasonal" in the "Category" field
    And I should see "false" in the "Available" dropdown
    And I should see "Get 20% off" in the "Promotype" dropdown
    And I should not see "Buy one, get one free" in the "Promotype" dropwdown