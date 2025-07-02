$(function() {
    function updateChatBoxVisibility() {
        var $chatBox = $('#chat-box');
        if ($chatBox.children().length > 0) {
            $chatBox.addClass('show');
        } else {
            $chatBox.removeClass('show');
        }
    }

    let currentChatId = null;
    let chatIdToDelete = null;

    function fetchChats() {
        return fetch('/api/chats').then(res => res.json());
    }

    function renderChatsSidebar(chats) {
        const $recent = $('#recent-chats');
        $recent.empty();
        chats.forEach(chat => {
            const li = $('<li>').attr('data-id', chat.id);
            if (chat.id === currentChatId) li.addClass('active');
            li.append($('<span>').text(chat.name));
            const delBtn = $('<button class="delete-chat-btn" title="Delete chat" style="float:right;background:none;border:none;cursor:pointer;margin-left:8px;padding:0;">' +
                "<i class='fa fa-trash' style='color:#ff6b6b;font-size:1.1em;'></i>" + '</button>');
            delBtn.on('click', function(e) {
                e.stopPropagation();
                chatIdToDelete = chat.id;
                $('#delete-modal').addClass('show');
            });
            li.append(delBtn);
            $recent.append(li);
        });
    }

    function fetchAndRenderChats() {
        fetchChats().then(chats => {
            renderChatsSidebar(chats);
        });
    }

    function fetchChatHistory(chatId) {
        return fetch(`/api/chats/${chatId}`).then(res => res.json());
    }

    function renderChatHistory(history) {
        const $chatBox = $('#chat-box');
        $chatBox.empty();
        history.slice().reverse().forEach(msg => {
            const who = msg.role === 'user' ? 'user' : 'bot';
            $chatBox.append(`<div class="msg ${who}"><div class="bubble">` + replaceTripleBacktickBlocks(msg.content) + `</div>`);
        });
        updateChatBoxVisibility();
        $chatBox.scrollTop($chatBox[0].scrollHeight);

        // ✅ Auto-highlight code
        setTimeout(() => {
            document.querySelectorAll('pre code').forEach(block => {
                block.innerHTML = block.innerHTML
                    .replace(/&lt;/g, "<")
                    .replace(/&gt;/g, ">")
                    .replace(/&amp;/g, "&");
                hljs.highlightElement(block);
            });
        }, 0);
    }


    function replaceTripleBacktickBlocks(text) {
        const tripleTickRegex = /```(\w+)?\n([\s\S]*?)```/g;
        let codeCounter = 1;

        // Escape HTML characters
        function escapeHtml(str) {
            return str.replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
        }

        return text.replace(tripleTickRegex, (match, lang, code) => {
            const codeId = `code-block-${codeCounter++}`;
            const escapedCode = escapeHtml(code.trim());
            const languageClass = lang ? `language-${lang}` : '';

            return `
<div class="code-block-wrapper code-box">
    <button class="copy-btn" data-target="${codeId}">Copy</button>
    <pre><code id="${codeId}" class="${languageClass}">${escapedCode}</code></pre>
</div>`;
        });
    }



    function startNewChat(firstMsg) {
        return fetch('/api/chats', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: firstMsg })
        }).then(res => res.json()).then(chat => {
            $('.sidebar').removeClass('open');
            $('#sidebar-overlay').removeClass('active');
            return chat;
        });
    }

    $(document).on('click', '#recent-chats li', function() {
        const chatId = $(this).attr('data-id');
        if (chatId === currentChatId) return;
        currentChatId = chatId;
        $('#recent-chats li').removeClass('active');
        $(this).addClass('active');
        fetchChatHistory(chatId).then(renderChatHistory);
        $('.sidebar').removeClass('open');
        $('#sidebar-overlay').removeClass('active');
    });

    fetchAndRenderChats();

    let isFirstChat = true;
    let firstMsgBuffer = '';

    $('#chat-form').on('submit', function(e) {
        e.preventDefault();
        var msg = $('#message').val();
        if (!msg.trim()) return;

        if (!currentChatId) {
            startNewChat(msg).then(chat => {
                currentChatId = chat.id;
                fetchAndRenderChats();
                renderChatHistory([{ role: 'user', content: msg }]);
                $('#message').val('');
                $('#chat-box').scrollTop($('#chat-box')[0].scrollHeight);
                updateChatBoxVisibility();
                sendMessageToChat(msg);
            });
            return;
        }

        $('#chat-box').append('<div class="msg user"><div class="bubble">' + $('<div>').text(msg).html() + '</div></div>');
        $('#message').val('');
        $('#chat-box').scrollTop($('#chat-box')[0].scrollHeight);
        updateChatBoxVisibility();
        sendMessageToChat(msg);
    });

    function sendMessageToChat(msg) {
        const chatBox = document.getElementById('chat-box');
        const botMsg = document.createElement('div');
        botMsg.className = 'msg bot';
        const botBubble = document.createElement('div');
        botBubble.className = 'bubble';
        botMsg.appendChild(botBubble);
        chatBox.appendChild(botMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
        updateChatBoxVisibility();

        let codeBlockBuffer = null;
        let codeBlockLang = '';
        let codeBlockElem = null;
        let codeBlockId = '';
        let botContentBuffer = '';

        function renderCodeLines(code) {
            const lines = code.replace(/</g, '&lt;').replace(/>/g, '&gt;').split(/\r?\n/);
            return lines.map((line) => `<span class="code-line">${line || '&nbsp;'}</span>`).join('');
        }

        function appendContentWithCodeHighlight(target, content) {
            if (codeBlockBuffer !== null) {
                const endIdx = content.indexOf('```');
                if (endIdx !== -1) {
                    codeBlockBuffer += content.slice(0, endIdx);
                    if (codeBlockElem) {
                        codeBlockElem.innerHTML = renderCodeLines(codeBlockBuffer);
                        if (window.hljs) hljs.highlightElement(codeBlockElem);
                    }
                    codeBlockBuffer = null;
                    codeBlockLang = '';
                    codeBlockElem = null;
                    codeBlockId = '';
                    const after = content.slice(endIdx + 3);
                    if (after) target.insertAdjacentHTML('beforeend', $('<div>').text(after).html());
                } else {
                    codeBlockBuffer += content;
                    if (codeBlockElem) {
                        codeBlockElem.innerHTML = renderCodeLines(codeBlockBuffer);
                        if (window.hljs) hljs.highlightElement(codeBlockElem);
                    }
                }
                return;
            }

            let idx = 0;
            while (idx < content.length) {
                const startIdx = content.indexOf('```', idx);
                if (startIdx === -1) {
                    target.insertAdjacentHTML('beforeend', $('<div>').text(content.slice(idx)).html());
                    break;
                }
                if (startIdx > idx) {
                    target.insertAdjacentHTML('beforeend', $('<div>').text(content.slice(idx, startIdx)).html());
                }

                let lang = '';
                let codeStart = startIdx + 3;
                const newlineIdx = content.indexOf('\n', codeStart);
                if (newlineIdx !== -1 && newlineIdx - codeStart < 10) {
                    lang = content.slice(codeStart, newlineIdx).trim();
                    codeStart = newlineIdx + 1;
                }

                const endIdx = content.indexOf('```', codeStart);
                if (endIdx !== -1) {
                    const code = content.slice(codeStart, endIdx);
                    const codeId = 'code-' + Math.random().toString(36).substr(2, 9);
                    const codeHtml = `<div class="code-block-wrapper code-box"><button class="copy-btn" data-target="${codeId}">Copy</button><pre><code id="${codeId}" class="${lang ? 'language-' + lang : ''}"></code></pre></div>`;
                    target.insertAdjacentHTML('beforeend', codeHtml);
                    const codeElem = document.getElementById(codeId);
                    if (codeElem) {
                        codeElem.innerHTML = renderCodeLines(code);
                        if (window.hljs) hljs.highlightElement(codeElem);
                    }
                    idx = endIdx + 3;
                } else {
                    codeBlockBuffer = content.slice(codeStart);
                    codeBlockLang = lang;
                    codeBlockId = 'code-' + Math.random().toString(36).substr(2, 9);
                    const codeHtml = `<div class="code-block-wrapper code-box"><button class="copy-btn" data-target="${codeBlockId}">Copy</button><pre><code id="${codeBlockId}" class="${lang ? 'language-' + lang : ''}"></code></pre></div>`;
                    target.insertAdjacentHTML('beforeend', codeHtml);
                    codeBlockElem = document.getElementById(codeBlockId);
                    if (codeBlockElem) {
                        codeBlockElem.innerHTML = renderCodeLines(codeBlockBuffer);
                        if (window.hljs) hljs.highlightElement(codeBlockElem);
                    }
                    hljs.highlightAll();
                    break;
                }
            }
        }

        fetch(`/api/chats/${currentChatId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        }).then(response => {
            if (!response.body) throw new Error('No response body');
            const reader = response.body.getReader();
            let decoder = new TextDecoder();
            let buffer = '';
            let errorShown = false;


            function readChunk() {
                return reader.read().then(({ done, value }) => {
                    if (done) {
                        updateChatBoxVisibility();
                        fetchAndRenderChats();
                        return;
                    }

                    buffer += decoder.decode(value, { stream: true });

                    // Process each full line (each JSON object is on its own line)
                    let lines = buffer.split('\n');
                    buffer = lines.pop(); // Save incomplete line for next read

                    for (let line of lines) {
                        line = line.trim();
                        if (!line) continue;

                        try {
                            const data = JSON.parse(line);
                            if (data.error && !errorShown) {
                                botBubble.innerHTML = '<span style="color:#ff6b6b;">' + data.error + '</span>';
                                errorShown = true;
                                updateChatBoxVisibility();
                                return;
                            }

                            if (
                                data.message &&
                                typeof data.message.content === 'string' &&
                                !errorShown
                            ) {
                                const chunkText = data.message.content;
                                botContentBuffer += chunkText;
                                appendContentWithCodeHighlight(botBubble, chunkText);
                                chatBox.scrollTop = chatBox.scrollHeight;
                            }
                        } catch (e) {
                            if (!errorShown) {
                                botBubble.innerHTML = '<span style="color:#ff6b6b;">Error parsing server response.</span>';
                                errorShown = true;
                                updateChatBoxVisibility();
                                return;
                            }
                        }
                    }

                    return readChunk(); // Continue reading
                }).catch(err => {
                    if (!errorShown) {
                        botBubble.innerHTML = '<span style="color:#ff6b6b;">' + (err.message || 'Error contacting server.') + '</span>';
                        errorShown = true;
                        updateChatBoxVisibility();
                    }
                });
            }

            return readChunk();
        }).catch((err) => {
            botBubble.innerHTML = '<span style="color:#ff6b6b;">' + (err.message || 'Error contacting server.') + '</span>';
            updateChatBoxVisibility();
        });
    }

    updateChatBoxVisibility();

    const messageInput = document.getElementById('message');
    if (messageInput) {
        messageInput.addEventListener('focus', function() {
            setTimeout(() => {
                messageInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        });
    }

    $(document).on('click', '.copy-btn', function() {
        const codeId = $(this).data('target');
        const codeElem = document.getElementById(codeId);
        if (codeElem) {
            const text = codeElem.innerText;
            navigator.clipboard.writeText(text).then(() => {
                const btn = this;
                const orig = btn.textContent;
                btn.textContent = 'Copied!';
                btn.disabled = true;
                setTimeout(() => {
                    btn.textContent = orig;
                    btn.disabled = false;
                }, 1200);
            });
        }
    });

    $(document).on('click', '#new-chat-btn', function() {
        currentChatId = null;
        $('#chat-box').empty();
        $('#chat-box').append(`
            <section class="quick-actions" id="quick-actions">
                <div class="greeting greeting-center">
                    <span class="greeting-hello">Hello <span id="user-name">User</span></span><br>
                    <span class="greeting-sub">How can I help you today?</span>
                </div>
                <div class="action-card">
                    <div class="action-icon">🕑</div>
                    <div class="action-title">What's Happen in 24 hours?</div>
                    <div class="action-desc">See what's been happening in the world over the last 24 hours</div>
                </div>
                <div class="action-card">
                    <div class="action-icon">📈</div>
                    <div class="action-title">Stock market update</div>
                    <div class="action-desc">See what's happening in the stock market in real time</div>
                </div>
                <div class="action-card">
                    <div class="action-icon">🔍</div>
                    <div class="action-title">Deep economic research</div>
                    <div class="action-desc">See research from experts that we have simplified</div>
                </div>
            </section>
        `);
        updateChatBoxVisibility();
        $('#recent-chats li').removeClass('active');
        $('#message').val('').focus();
        $('.sidebar').removeClass('open');
        $('#sidebar-overlay').removeClass('active');
    });

    $(document).on('click', '#cancel-delete-btn', function() {
        chatIdToDelete = null;
        $('#delete-modal').removeClass('show');
    });
    $(document).on('click', '#confirm-delete-btn', function() {
        if (!chatIdToDelete) return;
        const id = chatIdToDelete;
        $('#delete-modal').removeClass('show');
        fetch(`/api/chats/${id}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (currentChatId === id) {
                        currentChatId = null;
                        $('#chat-box').empty();
                        $('#chat-box').append(`
                            <section class="quick-actions" id="quick-actions">
                                <div class="greeting greeting-center">
                                    <span class="greeting-hello">Hello <span id="user-name">User</span></span><br>
                                    <span class="greeting-sub">How can I help you today?</span>
                                </div>
                                <div class="action-card">
                                    <div class="action-icon">🕑</div>
                                    <div class="action-title">What's Happen in 24 hours?</div>
                                    <div class="action-desc">See what's been happening in the world over the last 24 hours</div>
                                </div>
                                <div class="action-card">
                                    <div class="action-icon">📈</div>
                                    <div class="action-title">Stock market update</div>
                                    <div class="action-desc">See what's happening in the stock market in real time</div>
                                </div>
                                <div class="action-card">
                                    <div class="action-icon">🔍</div>
                                    <div class="action-title">Deep economic research</div>
                                    <div class="action-desc">See research from experts that we have simplified</div>
                                </div>
                            </section>
                        `);
                        updateChatBoxVisibility();
                    }
                    fetchAndRenderChats();
                }
            });
        chatIdToDelete = null;
    });

    $(document).on('click', '#close-btt', function() {
        $('#qr-modal').removeClass('show');
    });

    $(document).on('click', '#share-qr', function() {
        $('#qr-modal').addClass('show');
    });
});