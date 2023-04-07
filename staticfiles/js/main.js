/* The current country and contry */
let countries = []
let categories = [];
let countryList = document.getElementById("country-list");
let countryItem = document.getElementsByClassName("country-select")[0];
let categoryList = document.getElementById("category-list");

let categoryItem = document.getElementById("id-category");

const MARKER_PATH =
    "https://developers.google.com/maps/documentation/javascript/images/marker_green";
let autocomplete;

function initMap() {
    console.log("The countries", countries)
    var map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: -33.8688, lng: 151.2195}, zoom: 13
    });
    var input = document.getElementById('search-map');
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

    /* country set */

    var types = countries.map(function (country) {
        return country.toLowerCase();
    });

    autocomplete = new google.maps.places.Autocomplete(input, types);

    var options = {
        componentRestrictions: {country: types}
    };
    autocomplete.setOptions(options);

    autocomplete.bindTo('bounds', map);

    var infowindow = new google.maps.InfoWindow();
    var marker = new google.maps.Marker({
        map: map, anchorPoint: new google.maps.Point(0, -29)
    });
    console.log("reach here 111")

    autocomplete.addListener('place_changed', function () {
        // update auto complete
        //end
        infowindow.close();
        marker.setVisible(false);
        console.log("reach here", autocomplete)
        var place = autocomplete.getPlace();
        if (!place.geometry) {
            window.alert("Autocomplete returned place contains no geometry");

            autocomplete.setComponentRestrictions({
                country: [],
            });
            return;
        }

        console.log("The place", place)


        // Make request to backend API and Save the data
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function () {
            if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                var response = JSON.parse(xhr.responseText);

                console.log("the response", response.results[0].geometry.location.lat)

                // Move map to location
                map.setCenter({
                    lat: response.results[0].geometry.location.lat,
                    lng: response.results[0].geometry.location.lng
                });
                map.setZoom(17);
                marker.setPosition({lat: response.results[0].geometry.lat, lng: response.results[0].geometry.lng});
                marker.setVisible(true);

            }
        };
        xhr.open('GET', '/place_detail?query=' + encodeURIComponent(place.name));
        xhr.send();


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
        // Get the first photo for the place
        const photoUrl = place.photos && place.photos.length ? place.photos[0].getUrl() : '';

        // Set the image source of the place-image element
        const placeImage = document.getElementById('place-image');
        placeImage.src = photoUrl;

        // add the item to the database

    });


    countryItem.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {

            autocomplete.setComponentRestrictions({
                country: countries,
            });
        }
    });


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
    console.log(value.slice(0, 2))
    countries.push(value.slice(0, 2));
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


/* For category */

categoryItem.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        addCategoryItem();
        // rest the item if added
        categoryItem.value = ""
    }

})

function addCategoryItem() {
    const value = categoryItem.value.trim();

    if (!value) {
        return;
    }
    categories.push(value);
    renderCategoryItems();
    console.log(countries)
}

function renderCategoryItems() {
    categoryList.innerHTML = "";

    for (let i = 0; i < categories.length; i++) {
        const item = categories[i];

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
            removeCategoryItem(i);
        });

        categoryList.appendChild(itemNode);
    }
}

function removeCategoryItem(index) {
    categories.splice(index, 1);
    renderCategoryItems();
}

/*End category */


function searchAllPlaces() {
    // Make request to backend API and Save the data
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            var response = JSON.parse(xhr.responseText);
            alert("Collecting History data.")
        }
    };
    let input = document.getElementById('search-map').value;

    if (input === "") {
        alert("Search value is currently empty")
    } else {
        xhr.open('GET', '/search?query=' + encodeURIComponent(input) + "&category=" + categories);
        xhr.send();
    }
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

