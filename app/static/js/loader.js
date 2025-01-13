// Get form and loader elements
const form = document.getElementById('upload-form');
const loaderContainer = document.createElement('div');
loaderContainer.className = 'loader-container';

// Add loader container to body
document.body.appendChild(loaderContainer);

// Create loader HTML structure
loaderContainer.innerHTML = `
    <div class="loader">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
    </div>
    <div class="text"></div>
`;

// Define loading messages specific to keynotes generation
const loadingMessages = [
    "Analyzing document content and structure...",
    "Natural Language Processing helps identify key concepts and main ideas in your text.",
    "Text summarization algorithms work to extract the most important information.",
    "Machine learning models help identify topic hierarchies and relationships.",
    "Advanced algorithms identify important definitions, examples, and supporting details.",
    "Knowledge graphs help establish connections between related concepts.",
    "Semantic analysis ensures accurate understanding of context and meaning.",
    "Organizing information into a clear, hierarchical structure...",
    "Formatting your keynotes for optimal readability and understanding...",
    "Adding visual markers and emphasis to highlight key points...",
    "Finalizing your keynotes..."
];

// Create text elements dynamically
const textContainer = loaderContainer.querySelector('.text');
textContainer.innerHTML = ''; // Clear existing text divs
loadingMessages.forEach(message => {
    const div = document.createElement('div');
    div.textContent = message;
    textContainer.appendChild(div);
});

// Hide loader initially
loaderContainer.classList.add('hidden');

// Add form submit handler
form.addEventListener('submit', function(e) {
    e.preventDefault();

    // Validate form field
    const pageNum = document.getElementById('page-num').value;

    if (!pageNum) {
        alert('Please enter a page number');
        return;
    }

    // Show loader
    loaderContainer.classList.remove('hidden');

    // Initialize text animation
    let currentTextIndex = 0;
    const textElements = textContainer.querySelectorAll('div');
    
    // Initially hide all text elements except the first one
    textElements.forEach((el, index) => {
        if (index === 0) {
            el.style.opacity = '1';
            el.style.visibility = 'visible';
        } else {
            el.style.opacity = '0';
            el.style.visibility = 'hidden';
        }
    });

    // Function to smoothly transition to next text
    function showNextText() {
        const currentElement = textElements[currentTextIndex];
        const nextIndex = (currentTextIndex + 1) % textElements.length;
        const nextElement = textElements[nextIndex];

        // Make next element visible but transparent
        nextElement.style.visibility = 'visible';
        nextElement.style.opacity = '0';

        // Fade out current text while fading in next text
        requestAnimationFrame(() => {
            currentElement.style.opacity = '0';
            nextElement.style.opacity = '1';
            
            // After transition is complete, hide the old element
            setTimeout(() => {
                currentElement.style.visibility = 'hidden';
            }, 1000);
        });

        currentTextIndex = nextIndex;
    }

    // Calculate timings
    const messageInterval = 12000; // 12 seconds per message
    const totalDuration = 120000; // 2 minutes total
    
    // Start text rotation
    const textInterval = setInterval(showNextText, messageInterval);

    // Loop the messages if needed to fill the 2-minute duration
    setTimeout(() => {
        clearInterval(textInterval);
        currentTextIndex = 0; // Reset to first message
        
        // Start a new interval for the remaining time if needed
        if (messageInterval * loadingMessages.length < totalDuration) {
            const remainingInterval = setInterval(showNextText, messageInterval);
            
            // Clear the remaining interval and submit form after 2 minutes
            setTimeout(() => {
                clearInterval(remainingInterval);
                form.submit();
            }, totalDuration - (messageInterval * loadingMessages.length));
        } else {
            form.submit();
        }
    }, Math.min(messageInterval * loadingMessages.length, totalDuration));
});