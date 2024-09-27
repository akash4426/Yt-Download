document.getElementById('youtubeForm').addEventListener('submit', async function (event) {
    event.preventDefault();  

    const url = document.getElementById('box').value;  

    if (!isValidYouTubeURL(url)) {
        displayMessage('Please enter a valid YouTube URL.', 'error');
        return;
    }

    try {
        setLoadingState(true);
        const formData = new FormData();
        formData.append('url', url);  

        const response = await fetch('http://localhost:8000/download', {  
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Response:', result);
            displayMessage(result.message, 'success');
            if (result.download_url) {
                createDownloadLink(result.download_url);
            }
        } else {
            console.error('Error:', response.statusText);
            displayMessage('Failed to download video.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        displayMessage('An error occurred. Please try again.', 'error');
    } finally {
        setLoadingState(false);
    }
});

function isValidYouTubeURL(url) {
    const regex = /^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$/;
    return regex.test(url);
}

function setLoadingState(isLoading) {
    const button = document.getElementById('butt');
    button.disabled = isLoading;
    button.textContent = isLoading ? 'Downloading...' : 'Download';
}

function displayMessage(message, type) {
    const messageBox = document.getElementById('messageBox');
    messageBox.textContent = message;
    messageBox.className = type;  
}

function createDownloadLink(url) {
    const link = document.createElement('a');
    link.href = url;
    link.textContent = 'Click here to download your video';
    link.target = '_blank';
    document.body.appendChild(link);  
}
