$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#recommendation_id").val(res.id);
        $("#recommendation_product_a_sku").val(res.product_a_sku);
        $("#recommendation_product_b_sku").val(res.product_b_sku);
        $("#recommendation_recommendation_type").val(res.recommendation_type);
        $("#recommendation_likes").val(res.likes);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#recommendation_id").val("");
        $("#recommendation_product_a_sku").val("");
        $("#recommendation_product_b_sku").val("");
        $("#recommendation_recommendation_type").val("");
        $("#recommendation_likes").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a recommendation
    // ****************************************

    $("#create-btn").click(function () {

        let product_a_sku = $("#recommendation_product_a_sku").val();
        let product_b_sku = $("#recommendation_product_b_sku").val();
        let recommendation_type = $("#recommendation_recommendation_type").val();

        let data = {
            "product_a_sku": product_a_sku,
            "product_b_sku": product_b_sku,
            "recommendation_type": recommendation_type
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Successfully created a recommendation")        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Recommendation
    // ****************************************

    $("#update-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();
        let product_a_sku = $("#recommendation_product_a_sku").val();
        let product_b_sku = $("#recommendation_product_b_sku").val();
        let recommendation_type = $("#recommendation_recommendation_type").val();

        let data = {
            "product_a_sku": product_a_sku,
            "product_b_sku": product_b_sku,
            "recommendation_type": recommendation_type
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/recommendations/${recommendation_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();

        if (!recommendation_id) {
            flash_message("Please select a recommendation to retrieve.");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/recommendations/${recommendation_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // List all Recommendations
    // ****************************************

    $("#list-btn").click(function () {
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: "/recommendations",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Recommendation ID</th>'
            table += '<th class="col-md-2">Product A SKU</th>'
            table += '<th class="col-md-2">Product B SKU</th>'
            table += '<th class="col-md-2">Recommendation type</th>'
            table += '<th class="col-md-2">Likes</th>'
            table += '</tr></thead><tbody>'
            let firstRecommendation = "";
            for (let i = 0; i < res.length; i++) {
                let recommendation = res[i];
                table += `<tr id="row_${i}"><td>${recommendation.id}</td><td>${recommendation.product_a_sku}</td><td>${recommendation.product_b_sku}</td><td>${recommendation.recommendation_type}</td><td>${recommendation.likes}</td></tr>`;
                if (i == 0) {
                    firstRecommendation = recommendation;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            if (firstRecommendation != "") {
                update_form_data(firstRecommendation)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });


 // ****************************************
    // Delete a Recommendation
    // ****************************************

    $("#delete-btn").click(function () {

        let recommendation_id = $("#recommendation_id").val();

        if (!recommendation_id) {
            flash_message("Please select a recommendation to delete.");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/recommendations/${recommendation_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Recommendation has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#pet_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Recommendation
    // ****************************************

    $("#search-btn").click(function () {

        let product_a_sku = $("#recommendation_product_a_sku").val();
        let recommendation_type = $("#recommendation_recommendation_type").val();

        let queryString = ""

        if (product_a_sku) {
            queryString += 'product_a_sku=' + product_a_sku
        }
       
        if (recommendation_type) {
            if (queryString.length > 0) {
                queryString += '&recommendation_type=' + recommendation_type
            } else {
                queryString += 'recommendation_type=' + recommendation_type
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/recommendations?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Recommendation ID</th>'
            table += '<th class="col-md-2">Product A SKU</th>'
            table += '<th class="col-md-2">Product B SKU</th>'
            table += '<th class="col-md-2">Recommendation type</th>'
            table += '<th class="col-md-2">Likes</th>'
            table += '</tr></thead><tbody>'
            let firstRecommendation = "";
            for(let i = 0; i < res.length; i++) {
                let recommendation = res[i];
                table +=  `<tr id="row_${i}"><td>${recommendation.id}</td><td>${recommendation.product_a_sku}</td><td>${recommendation.product_b_sku}</td><td>${recommendation.recommendation_type}</td><td>${recommendation.likes}</td></tr>`;
                if (i == 0) {
                    firstRecommendation = recommendation;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstRecommendation != "") {
                update_form_data(firstRecommendation)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
    // ****************************************
    // Like a Recommendation
    // ****************************************

$("#like-btn").click(function () {
    let recommendation_id = $("#recommendation_id").val();
    if (!recommendation_id) {
        flash_message("Please select a recommendation to like.");
        return;
    }

    $("#flash_message").empty();

    let ajax = $.ajax({
        type: "PUT",
        url: `/api/recommendations/${recommendation_id}/like`,
        contentType: "application/json"
    });

    ajax.done(function (res) {
        update_form_data(res);
        flash_message("Successfully liked the recommendation!");
    });

    ajax.fail(function (res) {
        flash_message(res.responseJSON.message);
    });
});
