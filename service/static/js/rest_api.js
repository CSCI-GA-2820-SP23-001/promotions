$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_name").val(res.name);
        $("#promotion_category").val(res.category);
        if (res.available == true) {
            $("#promotion_available").val("true");
        } else {
            $("#promotion_available").val("false");
        }
        $("#promotion_promotype").val(res.promotype);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_name").val("");
        $("#promotion_category").val("");
        $("#promotion_available").val("");
        $("#promotion_promotype").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Promotion
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#promotion_name").val();
        let category = $("#promotion_category").val();
        let available = $("#promotion_available").val() == "true";
        let promotype = $("#promotion_promotype").val();

        let data = {
            "name": name,
            "category": category,
            "available": available,
            "promotype": promotype,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/api/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
            headers: { 'X-Api-Key': "133b94898f9b6c07ede6296e0ec197f7" }
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Promotion
    // ****************************************

    $("#update-btn").click(function () {

        let promotion_id = $("#promotion_id").val();
        let name = $("#promotion_name").val();
        let category = $("#promotion_category").val();
        let available = $("#promotion_available").val() == "true";
        let promotype = $("#promotion_promotype").val();

        let data = {
            "name": name,
            "category": category,
            "available": available,
            "promotype": promotype,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/promotions/${promotion_id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
            headers: { 'X-Api-Key': "133b94898f9b6c07ede6296e0ec197f7" }
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Promotion
    // ****************************************

    $("#retrieve-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/promotions/${promotion_id}`,
            contentType: "application/json",
            data: '',
            headers: { 'X-Api-Key': "133b94898f9b6c07ede6296e0ec197f7" }
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
    // Delete a Promotion
    // ****************************************

    $("#delete-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/promotions/${promotion_id}`,
            contentType: "application/json",
            data: '',
            headers: { 'X-Api-Key': "133b94898f9b6c07ede6296e0ec197f7" }
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Promotion has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Promotion
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#promotion_name").val();
        let category = $("#promotion_category").val();
        let available = $("#promotion_available").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/promotions?${queryString}`,
            contentType: "application/json",
            data: '',
            headers: { 'X-Api-Key': "133b94898f9b6c07ede6296e0ec197f7" }
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Category</th>'
            table += '<th class="col-md-2">Available</th>'
            table += '<th class="col-md-2">Promotion Type</th>'
            table += '</tr></thead><tbody>'
            let firstPromotion = "";
            for (let i = 0; i < res.length; i++) {
                let promotion = res[i];
                table += `<tr id="row_${i}"><td>${promotion.id}</td><td>${promotion.name}</td><td>${promotion.category}</td><td>${promotion.available}</td><td>${promotion.promotype}</td></tr>`;
                if (i == 0) {
                    firstPromotion = promotion;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPromotion != "") {
                update_form_data(firstPromotion)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

})
