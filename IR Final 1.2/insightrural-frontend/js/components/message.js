// Message Component - Creates chat message elements
const MessageComponent = {
    // Create a message element
    createMessage(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = sender === 'user' ? 'message-user' : 'message-bot';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Format content with line breaks
        const formattedContent = content.replace(/\n/g, '<br>');
        contentDiv.innerHTML = formattedContent;
        
        messageDiv.appendChild(contentDiv);
        
        return messageDiv;
    }
};