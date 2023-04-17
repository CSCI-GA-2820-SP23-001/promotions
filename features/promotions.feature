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

Scenario: List all promotions
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "BFFs" in the results
    And I should see "summer2023" in the results
    And I should not see "christimas" in the results