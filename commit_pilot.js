#!/usr/bin/env node

/**
 * ==============================================================================
 * COMMIT-PILOT: Smart Commit Message AI Architect (Conventional Commits Engine)
 * Automatically evaluates staged git changes and drafts a perfect semantic message.
 * ==============================================================================
 */

const { execSync } = require('child_process');
const http = require('http');

// --- ANSI UI Core Terminal Colors ---
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const BLUE = '\x1b[34m';
const CYAN = '\x1b[36m';
const BOLD = '\x1b[1m';
const RESET = '\x1b[0m';

function getGitDiff() {
    try {
        // Fetch only staged modifications to precisely draft semantic meanings
        const diff = execSync('git diff --cached', { encoding: 'utf-8' }).trim();
        return diff;
    } catch (error) {
        console.error(`${RED}[CRITICAL ERROR] Failed to fetch git staging configurations: ${error.message}${RESET}`);
        process.exit(1);
    }
}

function queryLocalLLM(diffContent, callback) {
    // Structured instruction prompt payload enforcement to keep responses deterministic
    const systemPrompt = "You are a professional software engineering git automation agent. Write a single, concise commit message following the strict 'Conventional Commits' specifications based on the code diff provided. Output ONLY the commit message string. Do not include quotes, greetings, markdown formatting, explanations, or any extra text. Format must be: <type>(<scope>): <short summary>. Examples: 'feat(auth): add password hashing validation', 'fix(api): repair database timeout on cluster connections'.";
    
    const payload = JSON.stringify({
        model: 'llama3:latest', // Uses universal Llama3 model footprint via Ollama core
        prompt: `${systemPrompt}\n\nCode changes diff:\n${diffContent}`,
        stream: false
    });

    const options = {
        hostname: '127.0.0.1',
        port: 11434, // Standard default Ollama microservice connection gateway port
        path: '/api/generate',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(payload)
        }
    };
    const req = http.request(options, (res) => {
        let responseBody = '';
        res.setEncoding('utf-8');
        res.on('data', (chunk) => responseBody += chunk);
        res.on('end', () => {
            try {
                const parsed = JSON.parse(responseBody);
                if (parsed.response) {
                    callback(parsed.response.trim());
                } else {
                    console.error(`${RED}[AI REJECTED] Malformed JSON payload returned from local LLM model stream.${RESET}`);
                    process.exit(1);
                }
            } catch (e) {
                console.error(`${RED}[PARSE FAILURE] Unable to parse target response: ${e.message}${RESET}`);
                process.exit(1);
            }
        });
    });

    req.on('error', (e) => {
        console.error(`\n${RED}[OLLAMA OFFLINE] Unable to connect to local AI server at http://127.0.0.1:11434${RESET}`);
        console.error(`${YELLOW}👉 Superpower check failed! Ensure Ollama app is actively running and you pulled the model via: 'ollama run llama3'${RESET}`);
        process.exit(1);
    });

    req.write(payload);
    req.end();
}

function runCommitPilot() {
    console.log(`${CYAN}${BOLD}[Commit-Pilot Core Analyzing Git Diff...]${RESET}`);
    const stagedChanges = getGitDiff();

    if (!stagedChanges) {
        console.log(`${YELLOW}[!] No staged adjustments discovered. Add your project modifications using 'git add' first.${RESET}`);
        process.exit(0);
    }

    console.log(`${BLUE}[i] Dispatching payload to local AI cluster environment...${RESET}`);
    queryLocalLLM(stagedChanges, (aiCommitMessage) => {
        console.log(`\n${GREEN}✔ Generated Perfect Semantic Message:${RESET}`);
        console.log(`${BOLD}${WHITE}"${aiCommitMessage}"${RESET}\n`);
        
        try {
            // Hot-injects the generated AI message inside git core execution pipelines hooks
            execSync(`git commit -m "${aiCommitMessage.replace(/"/g, '\\"')}"`, { stdio: 'inherit' });
            console.log(`\n${GREEN}${BOLD}[SUCCESS] Changeset committed securely via Commit-Pilot architecture!${RESET}`);
        } catch (err) {
            console.error(`${RED}[TRANSACTION FAILED] Git commit processing terminated prematurely.${RESET}`);
            process.exit(1);
        }
    });
}

runCommitPilot();
