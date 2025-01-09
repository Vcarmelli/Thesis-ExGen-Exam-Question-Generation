const target = document.querySelector("#end-of-thumbnails");
const container = document.querySelector(".thumbnail-container");
const pagesInput = document.getElementById('page-num');
let selectedPages = [];
let isVisible = false;
let isLoading = false;
let page = 10; 
let questionCount = 0;

addThumbnailListeners();


// Listen for manual input changes
pagesInput.addEventListener("input", () => handleManualInput());

// Handle manual input changes
function handleManualInput() {
    const inputValue = pagesInput.value;
    const inputPages = parseInputToPages(inputValue);

    // Remove selected class from all thumbnails
    const allThumbnails = document.querySelectorAll(".thumbnail-wrapper");
    allThumbnails.forEach((item) => {
        const pageNumber = parseInt(item.querySelector("p").textContent);
        
        const page = item.querySelector(".thumbnail-item");
        if (inputPages.includes(pageNumber)) {
            page.classList.add("selected");
        } else {
            page.classList.remove("selected");
        }
    });

    // Update the selectedPages array
    selectedPages = inputPages;
}

// Convert input string to array of page numbers
function parseInputToPages(input) {
    const pages = input.split(",").map(page => page.trim());
    let result = [];

    pages.forEach(page => {
        if (page.includes("-")) {
            const [start, end] = page.split("-").map(num => parseInt(num.trim(), 10));
            if (!isNaN(start) && !isNaN(end) && start <= end) {
                for (let i = start; i <= end; i++) {
                    result.push(i); // Add all numbers in the range
                }
            }
        } else {
            const singlePage = parseInt(page, 10);
            if (!isNaN(singlePage)) {
                result.push(singlePage); // Add single number
            }
        }
    });

    console.log("input in parseInputToPages:", input);
    console.log("result:", result);
    return result;
}


// FUNCTION FOR SELECTING PAGES
function addThumbnailListeners() {
    const thumbnailItems = document.querySelectorAll(".thumbnail-item");
    
    thumbnailItems.forEach((item, index) => {
        const pageNumber = index + 1; // Page numbers start at 1
        item.addEventListener("click", () => togglePageSelection(pageNumber, item));
    });
}


// params for MutationObserver
const config = { childList: true };

const newThumbnailListeners = (mutationList, moreThumbs) => {
    for (const mutation of mutationList) {
        for (const addedNode of mutation.addedNodes) {
            const pageNumber = parseInt(addedNode.querySelector("p").textContent); 
            const item = addedNode.querySelector(".thumbnail-item");
            addedNode.addEventListener("click", () => togglePageSelection(pageNumber, item));
        }
    }
};
// INITIALIZE OBSERVERS FOR THUMBNAIL LISTENERS
const newThumbs = new MutationObserver(newThumbnailListeners);
newThumbs.observe(container, config);


function togglePageSelection(pageNumber, item) {
    if (selectedPages.includes(pageNumber)) {
        selectedPages = selectedPages.filter(page => page !== pageNumber); // Remove if already selected
        item.classList.remove("selected"); 
    } else {
        selectedPages.push(pageNumber); // Add if not selected
        item.classList.add("selected"); 
    }
    pagesInput.value = formatPageNumbers(selectedPages);
}

function formatPageNumbers(pages) {
    const uniquePages = [...new Set(pages)].sort((a, b) => a - b);
    const result = [];

    for (let i = 0; i < uniquePages.length; i++) {
        const start = uniquePages[i];
        while (i < uniquePages.length - 1 && uniquePages[i + 1] === uniquePages[i] + 1) {
            i++;
        }
        const end = uniquePages[i];
        result.push(start === end ? `${start}` : `${start}-${end}`);
    }

    return result.join(", ");
}



// FUNCTIONS FOR LOADING THUMBNAIL
async function fetchThumbnails(startIndex) {
    // Fetch the next set of thumbnails
    const response = await fetch(`/selection/${startIndex}`);
    const data = await response.json();
    return data.thumbnails || [];
}

function appendThumbnails(thumbnails, page) {
    // Append each new thumbnail to the container
    thumbnails.forEach((thumbnail, index) => {
        const thumbnailWrapper = document.createElement("div");
        thumbnailWrapper.classList.add("thumbnail-wrapper");

        const thumbnailItem = document.createElement("div");
        thumbnailItem.classList.add("thumbnail-item");

        const img = document.createElement("img");
        img.src = `../static/thumbnails/${thumbnail}`;
        thumbnailItem.appendChild(img);
        thumbnailWrapper.appendChild(thumbnailItem);

        const pageNumber = document.createElement("p");
        pageNumber.textContent = page + (index + 1) ;
        thumbnailWrapper.appendChild(pageNumber);

        container.insertBefore(thumbnailWrapper, target);
    });
}


// params for IntersectionObserver
const options = {
    root: container,
    rootMargin: "100px"
}

const loadThumbnails = async (entries) => {
    isVisible = entries[0].isIntersecting;
    if (!isVisible || isLoading) return; // prevent duplicate pages
    
    isLoading = true;
    try {
        const thumbnails = await fetchThumbnails(page);
        if (thumbnails.length > 0) {
            appendThumbnails(thumbnails, page);
            page += 10;
        } else {
            // Stop observing if no more thumbnails and hide loader
            target.style.display = 'none';
            observer.unobserve(target);
        }
    } catch (error) {
        console.error("Error fetching thumbnails:", error);
    } finally {
        isLoading = false;
    }
};

// INITIALIZE END-OF-THUMBNAIL OBSERVER
const observer = new IntersectionObserver(loadThumbnails, options);
observer.observe(target);