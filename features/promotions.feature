Feature: The promotion service back-end
    As a Marketing Manager
    I need a RESTful catalog service
    So that I can keep track of all the promotions

Background:
    Given the following promotions
        | name       | category           | available | promotype            |
        | christimas | holiday            | False     | BUYONEGETONEFREE     | 
        | BFFs       | friends_and_family | True      | GET20PERCENTOFF      |
        | summer2023 | seasonal           | True      | UNKNOWN              |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotions!" in the title
    And I should not see "404 Not Found"

Scenario: Create a Promotion
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
    And I should not see "christimas" in the results