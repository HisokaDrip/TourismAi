let spotsData = [];

// Function to search for tourist spots
async function searchLocation() {
  const location = document.getElementById("searchInput").value;
  const resultsContainer = document.getElementById("touristList");

  try {
    const response = await fetch('/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ location }),
    });

    if (response.ok) {
      spotsData = await response.json();
      displaySpots(spotsData);
    } else {
      const errorMessage = await response.json();
      resultsContainer.innerHTML = `<li>${errorMessage.error}</li>`;
    }
  } catch (error) {
    console.error('Error fetching tourist spots:', error);
    resultsContainer.innerHTML = '<li>Failed to fetch tourist spots. Please try again later.</li>';
  }
}


// Function to display spots with category icons and Directions button
function displaySpots(spots) {
  const resultsContainer = document.getElementById("touristList");
  resultsContainer.innerHTML = ''; // Clear previous results

  spots.forEach((spot) => {
    const listItem = document.createElement("li");
    listItem.classList.add("spot-item");

    // Display the spot photo if available, else a placeholder
    const photo = document.createElement("img");
    photo.src = spot.photo_url || "/static/icons/question_mark.png";
    photo.alt = `${spot.name} photo`;
    photo.classList.add("spot-photo");

    // Fallback if the image fails to load
    photo.onerror = function () {
      this.src = "/static/icons/question_mark.png";
      this.onerror = null; // Ensure onerror is triggered only once
    };

    // Display the spot details without rating text
    const spotInfo = document.createElement("div");
    spotInfo.innerHTML = `
      <strong>${spot.name}</strong> - ${spot.address}
      <div class="rating">${getRatingStars(spot.rating)}</div>
    `;

    // Create "Directions" button with an icon and add the class "directions-button"
    const directionsButton = document.createElement("button");
    directionsButton.innerHTML = `<span class="directions-icon">📍</span> Directions`;
    directionsButton.classList.add("directions-button"); // Add this line

    // Get the destination latitude and longitude for directions
    directionsButton.onclick = () => openDirections(spot.latitude, spot.longitude);

    listItem.appendChild(photo);
    listItem.appendChild(spotInfo);
    listItem.appendChild(directionsButton); // Append the Directions button

    resultsContainer.appendChild(listItem);
  });
}

// Function to open directions in Google Maps to the specific destination
function openDirections(lat, lng, category) {
  // Send a POST request to record the click
  fetch('/click', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ category: category })
  })
  .then(response => response.json())
  .then(data => console.log(data.message))
  .catch(error => console.error('Error recording click:', error));

  // Open directions in Google Maps
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const userLat = position.coords.latitude;
        const userLng = position.coords.longitude;
        const googleMapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${lat},${lng}&travelmode=driving`;
        window.open(googleMapsUrl, "_blank");
      },
      (error) => {
        alert("Unable to access your location. Please ensure location access is enabled or try again.");
        console.error("Geolocation error:", error);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}

// Function to generate up to 5 stars for ratings, including half stars if needed
function getRatingStars(rating) {
  const maxStars = 5;
  const starsHTML = [];

  // Generate full stars
  for (let i = 0; i < Math.floor(rating); i++) {
      starsHTML.push('<span class="star full">⭐</span>');
  }

  // Generate half star if rating has a decimal of 0.5
  if (rating % 1 >= 0.5 && starsHTML.length < maxStars) {
      starsHTML.push('<span class="star half">⭐</span>');
  }

  // Fill remaining with empty stars to reach maxStars
  while (starsHTML.length < maxStars) {
      starsHTML.push('<span class="star empty">☆</span>');
  }

  return starsHTML.join('');
}

// Custom cursor effect
document.addEventListener("DOMContentLoaded", () => {
  const cursorInner = document.querySelector(".cursor-inner");
  const cursorOuter = document.querySelector(".cursor-outer");

  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let posX = mouseX;
  let posY = mouseY;

  document.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;

    cursorOuter.style.left = `${mouseX}px`;
    cursorOuter.style.top = `${mouseY}px`;
    cursorInner.style.left = `${mouseX}px`;
    cursorInner.style.top = `${mouseY}px`;
  });

  function animateCursors() {
    posX += (mouseX - posX) / 8;
    posY += (mouseY - posY) / 8;
    cursorOuter.style.left = `${posX}px`;
    cursorOuter.style.top = `${posY}px`;

    requestAnimationFrame(animateCursors);
  }

  animateCursors();

  // Add hover-zoom effect to all interactive elements, including Directions button
  const interactiveElements = document.querySelectorAll("button, a, input, .directions-button");
  interactiveElements.forEach((element) => {
    element.addEventListener("mouseenter", () => {
      cursorInner.classList.add("hover-zoom");
    });
    element.addEventListener("mouseleave", () => {
      cursorInner.classList.remove("hover-zoom");
    });
  });
});


// Function to go back to the initial home state (clear search results)
function goHome() {
  document.getElementById("searchInput").value = ""; // Clear the search input field
  const resultsContainer = document.getElementById("touristList");
  resultsContainer.innerHTML = ""; // Clear the search results
  spotsData = []; // Reset spotsData array
}

// Function to filter by category
function filterCategory(category) {
  if (category === 'all') {
    displaySpots(spotsData);
  } else {
    const filteredSpots = spotsData.filter(spot => spot.category === category);
    displaySpots(filteredSpots);
  }
}

// Function to sort by rating
function sortByRating() {
  const sortedSpots = [...spotsData].sort((a, b) => (b.rating || 0) - (a.rating || 0));
  displaySpots(sortedSpots);
}
