/* The current country and contry */
let countries = []
let countryList = document.getElementById("country-list");
let countryItem = document.getElementsByClassName("country-select")[0];
let categoryItem = document.getElementById("id-category");

let autocomplete;
// Create a container element for the suggestions for Country
let country_container = document.createElement('div');
country_container.classList.add('autocomplete-container');
let autocomplete_country = document.getElementById("autocomplete-country");
if (autocomplete_country) {
    autocomplete_country.appendChild(country_container);
} else {
    console.error("Element with ID 'autocomplete-country' not found.");
}

/* End create container element for country suggestion*/

// Create a container element for the suggestions for Country
let category_container = document.createElement('div');
let categoryList = document.getElementsByClassName('list-categories')[0]
category_container.classList.add('autocomplete-container');
let autocomplete_category = document.getElementById("autocomplete-category");
if (autocomplete_category) {
    autocomplete_category.appendChild(category_container);
} else {
    console.error("Element with ID 'autocomplete-category' not found.");
}

/* End create container element for category suggestion*/


function initMap() {
    console.log("The countries", countries)
    var map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: -33.8688, lng: 151.2195}, zoom: 13
    });

    var infowindow = new google.maps.InfoWindow();
    var marker = new google.maps.Marker({
        map: map, anchorPoint: new google.maps.Point(0, -29)
    });

    /* Event listen when typing category*/
    countryItem.addEventListener("input", (event) => {

        // Get the value of the input field

        // Make a request to the API
        var xhr = new XMLHttpRequest();
        xhr.open('GET', "/autocomplete" + '?query=' + encodeURIComponent(countryItem.value));
        xhr.onload = function () {
            if (xhr.status === 200) {
                // Parse the JSON response and display the suggestions
                var response = JSON.parse(xhr.responseText);
                var suggestions = response.predictions;
                country_container.innerHTML = '';
                suggestions.forEach(function (suggestion) {
                    var item = document.createElement('div');
                    item.classList.add('autocomplete-item');
                    item.textContent = suggestion.description;
                    item.addEventListener('click', function () {
                        countryItem.value = suggestion.description;
                        country_container.innerHTML = '';
                        // create the card image
                        CreateCardImage(suggestion.description)
                    });
                    country_container.appendChild(item);

                });

            }
        };
        xhr.send();
    });

    /* Event listen when typing country */
    categoryItem.addEventListener('input', () => {
        const inputText = categoryItem.value.toLowerCase();
        let counter = 0; // initialize a counter variable
        category_container.innerHTML = '';
        // loop through the options and hide the ones that don't match the input
        for (let i = 0; i < categoryList.options.length; i++) {
            const option = categoryList.options[i];
            const optionText = option.value.toLowerCase();
            if (optionText.indexOf(inputText) !== -1) {
                const item = document.createElement('div');
                item.classList.add('autocomplete-item');
                item.textContent = optionText;
                item.addEventListener('click', () => {
                    categoryItem.value = optionText;
                    category_container.innerHTML = '';
                });
                category_container.appendChild(item);
                counter++; // increment the counter
                if (counter === 30) { // break the loop once the counter reaches 5
                    break;
                }
            }
        }
    })

    /* ENd listener*/

    function CreateCardImage(search_query) {
        // update auto complete
        //end
        infowindow.close();
        marker.setVisible(false);

        // Make request to backend API and Save the data
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '/place_detail?query=' + encodeURIComponent(search_query));
        xhr.onreadystatechange = function () {
            if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                var response = JSON.parse(xhr.responseText);
                let place = response

                console.log("the response", place)

                // Move map to location
                map.setCenter({
                    lat: response.geometry.location.lat,
                    lng: response.geometry.location.lng
                });
                map.setZoom(17);
                marker.setPosition({lat: response.geometry.lat, lng: response.geometry.lng});
                marker.setVisible(true);

                var address = '';
                if (place.address_components) {
                    address = [(place.address_components[0] && place.address_components[0].short_name || ''), (place.address_components[1] && place.address_components[1].short_name || ''), (place.address_components[2] && place.address_components[2].short_name || '')].join(' ');
                }

                infowindow.setContent('<div><strong>' + place.name + '</strong><br>' + address);
                infowindow.open(map, marker);


                document.getElementById('place-name').innerHTML = place.name;
                document.getElementById('place-address').innerHTML = place.formatted_address;
                document.getElementById('place-phone').innerHTML = place.formatted_phone_number || 'Phone number not available';
                document.getElementById('place-website').innerHTML = `<a href="${place.website}" target="_blank" class="btn btn-md" style="">View More</a>` || 'Website not available';
                // Set the image source of the place-image element
                const placeImage = document.getElementById('place-image');
                placeImage.src = place.photo;

                // add the item to the database

            }
        };
        xhr.send();
    }

}

/* For country*/
countryItem.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();

        addCountryItem();
    }
});

function addCountryItem() {
    const value = countryItem.value.trim();

    if (!value) {
        return;
    }
    console.log(value)
    countries.push(value.replace(/,/g, ' '));
    countryItem.value = "";

    renderCountryItems();
    console.log(countries)
}

function removeCountryItem(index) {
    countries.splice(index, 1);
    renderCountryItems();
}

function renderCountryItems() {
    countryList.innerHTML = "";

    for (let i = 0; i < countries.length; i++) {
        const item = countries[i];

        const itemNode = document.createElement("div");
        itemNode.className = "d-flex align-items-center list-container custom-flex-item";
        itemNode.innerHTML = `
          <div class="list-item" style="background-color: #b9b6b6;border-radius: 10px;padding: 5px">
            <span class="text-dark " style="padding-right: 2px;">${item}</span>
            <button class="cancel-btn  p-0 text-dark " 
            style="background-color: gray;border-radius: 50%;padding: 10px;    width: 25px;">x</button>
          </div>
    `;

        const cancelBtn = itemNode.querySelector(".cancel-btn");
        cancelBtn.addEventListener("click", () => {
            removeCountryItem(i);
        });

        countryList.appendChild(itemNode);
    }
}

/*End Country*/


function searchAllPlaces() {
    // Make request to backend API and Save the data
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            var response = JSON.parse(xhr.responseText);
            alert("Collecting History data.")
        }
    };

    xhr.open('GET', '/search' + '?category=' + categoryItem.value + '&query=' + encodeURIComponent(JSON.stringify(countries)));
    xhr.send();

}

function getCookie(name) {
    var cookieValue = null;

    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');

        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);

            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}


/* Category Auto Complete*/


/*ENd Auto Complete*/

