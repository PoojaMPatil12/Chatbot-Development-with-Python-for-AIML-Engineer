document.getElementById("upload-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const fileInput = document.getElementById("pdf-file");
    const userQuery = document.getElementById("user-query").value;
    
    if (!fileInput.files.length) {
        alert("Please upload a PDF file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("user_query", userQuery);

    try {
        const response = await fetch("http://localhost:8000/upload/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        document.getElementById("chatbot-response").innerText = data.chatbot_response || "No response.";
    } catch (error) {
        document.getElementById("chatbot-response").innerText = "Error: Unable to fetch response.";
    }
});
