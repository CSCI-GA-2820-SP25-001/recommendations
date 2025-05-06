    Feature: The recommendation service back-end
        As a Recommendation Manager
        I need a RESTful catalog service
        So that I can keep track of all recommendations

    Background:
        Given the following Recommendations
            | product_a_sku | product_b_sku | recommendation_type | likes |
            | HYJtLnYf      | cUnyEDwP      | CROSS_SELL          | 0     |
            | GQGEsdfq      | cUafQfef      | CROSS_SELL          | 0     |
            | FQEFQrQs      | cEdasdTs      | UP_SELL             | 1     |
            | dasdfeaQ      | FefaffeQ      | BUNDLE              | 3     |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Recommendations Demo REST API Service" in the title
        And I should not see "404 Not Found"

    Scenario: List all Recommendations
        When I visit the "Home Page"
        And I press the "List" button
        Then I should see the message "Success"
        And I should see "HYJtLnYf" in the results
        And I should see "GQGEsdfq" in the results
        And I should see "FQEFQrQs" in the results
        And I should see "dasdfeaQ" in the results

    Scenario: Search for HYJtLnYf
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Product A SKU" to "HYJtLnYf"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "HYJtLnYf" in the results
        And I should not see "cEdasdTs" in the results
        And I should not see "FefaffeQ" in the results
        And I should not see "cUafQfef" in the results

    Scenario: Search for UP_SELL
        When I visit the "Home Page"
        And I press the "Clear" button
        And I select "UP_SELL" in the "Recommendation type" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "cEdasdTs" in the results
        And I should not see "cUnyEDwP" in the results
        And I should not see "cUafQfef" in the results
        And I should not see "FefaffeQ" in the results

    Scenario: Search for dasdfeaQ and BUNDLE
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Product A SKU" to "dasdfeaQ"
        And I select "BUNDLE" in the "Recommendation type" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "FefaffeQ" in the results
        And I should not see "cUnyEDwP" in the results
        And I should not see "cEdasdTs" in the results
        And I should not see "cUafQfef" in the results

    Scenario: Search for nonexistent recommendation: AfqrQtgQ
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Product A SKU" to "AfqrQtgQ"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should not see "HYJtLnYf" in the results
        And I should not see "cEdasdTs" in the results
        And I should not see "FefaffeQ" in the results
        And I should not see "cUafQfef" in the results

    Scenario: Create a Recommendation
        When I visit the "Home Page"
        And I set the "product_a_sku" to "Product_a"
        And I set the "product_b_sku" to "Product_b"
        And I select "CROSS_SELL" in the "recommendation_type" dropdown
        And I press the "Create" button
        Then I should see the message "Successfully created a recommendation"
        When I press the "Clear" button
        Then the "id" field should be empty
        And the "product_a_sku" field should be empty
        And the "product_b_sku" field should be empty
        And the "recommendation_type" field should be empty
        And the "likes" field should be empty
        When I visit the "Home Page"
        And I set the "product_a_sku" to "Product_a"
        And I set the "product_b_sku" to "Product_b"
        And I select "CROSS_SELL" in the "recommendation_type" dropdown
        And I press the "Create" button
        Then I should see the message "Recommendation already exists"

    Scenario: Delete a Recommendation
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Product A SKU" to "HYJtLnYf"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "HYJtLnYf" in the results
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Delete" button
        Then I should see the message "Recommendation has been Deleted!"
        When I press the "Clear" button
        And I set the "Product A SKU" to "HYJtLnYf"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should not see "HYJtLnYf" in the results
        When I press the "Clear" button
        And I set the "Id" to "12345"
        And I press the "Delete" button
        Then I should see the message "Recommendation has been Deleted!"
        When I press the "Clear" button

    Scenario: Retrieve recommendation
        When I visit the "Home Page"
        And I set the "product_a_sku" to "aSKU"
        And I set the "product_b_sku" to "bSKU"
        And I select "CROSS_SELL" in the "recommendation_type" dropdown
        And I press the "Create" button
        Then I should see the message "Successfully created a recommendation"
        When I copy the "Id" field
        And I press the "Clear" button
        Then the "id" field should be empty
        When I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "aSKU" in the "Product a sku" field
        And I should see "bSKU" in the "Product b sku" field
        And I should see "CROSS_SELL" in the "Recommendation type" field
        And I should see "0" in the "Likes" field
        When I press the "Clear" button
        And I set the "Id" to "123456"
        And I press the "Retrieve" button
        Then I should see the message "Recommendation with id '123456' was not found."

    Scenario: Update a Reccommendation
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Product A SKU" to "GQGEsdfq"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "GQGEsdfq" in the "Product A SKU" field
        And I should see "cUafQfef" in the "Product B SKU" field
        And I should see "CROSS_SELL" in the "Recommendation type" field
        When I change "Product A SKU" to "FWiNenfo"
        And I press the "Update" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "FWiNenfo" in the "Product A SKU" field
        When I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "FWiNenfo" in the results
        And I should not see "GQGEsdfq" in the results
        When I set the "Id" to "123456"
        And I set the "Product B SKU" to "SqefQGEs"
        And I press the "Update" button
        Then I should see the message "Recommendation with id '123456' was not found."

    Scenario: Like a recommendation increases like count
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Product A SKU" to "HYJtLnYf"
        And I press the "Search" button
        Then I should see the message "Success"
        When I press the "Like" button
        Then I should see "1" in the "Likes" field
        And I should see the message "Successfully liked the recommendation!"

    Scenario: Dislike a recommendation decreases like count
        When I visit the "Home Page"
        And I press the "Clear" button
        And I set the "Product A SKU" to "FQEFQrQs"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "FQEFQrQs" in the "Product A SKU" field
        And I should see "cEdasdTs" in the "Product B SKU" field
        And I should see "1" in the "Likes" field
        # When I press the "Dislike" button
        # Then I should see "0" in the "Likes" field
        # And I should see the message "Successfully disliked the recommendation!"
        # When I press the "Dislike" button
        # Then I should see the message "Likes cannot be negative"

    Scenario: Dislike a non-existent Recommendation
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Dislike" button
        Then I should see the message "Please select a recommendation to dislike."

    Scenario: Like a non-existent Recommendation
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Like" button
        Then I should see the message "Please select a recommendation to like."

    Scenario: Retrieve a non-existent Recommendation
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Retrieve" button
        Then I should see the message "Please select a recommendation to retrieve."

    Scenario: Delete a non-existent Recommendation
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Delete" button
        Then I should see the message "Please select a recommendation to delete."

    Scenario: Create with missing attributes
        When I visit the "Home Page"
        And I press the "Clear" button
        And I press the "Create" button
        Then I should see the message "Invalid value for RecommendationType: None"