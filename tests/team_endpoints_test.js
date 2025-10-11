import http from 'k6/http';
import { check, group } from 'k6';
import { Counter } from 'k6/metrics';
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.3.0/index.js';

// ✅ Custom metrics
const teamCreatedSuccess = new Counter('team_created_success');
const teamAlreadyExists = new Counter('team_already_exists');
const questionNotFound = new Counter('question_not_found');
const questionAlreadyAllotted = new Counter('question_already_allotted');

export const options = {
    vus: 100,           // 100 concurrent users
    duration: '30s',    // Run for exactly 30 seconds
};

export default function () {
    group('Team-Question Concurrency Test', function () {
        // Create unique team name for each iteration
        const teamname = `LoadTeam_${uuidv4()}`;
        
        // First create a question for this test
        const question_code = `Q_${uuidv4()}`;
        
        // Step 1: Create question
        const questionPayload = JSON.stringify({
            id: question_code,
            question: `Load test question for ${teamname}`
        });
        
        const questionRes = http.post(
            'http://localhost:8000/siamMPL/admin/questions/',
            questionPayload,
            { headers: { 'Content-Type': 'application/json' } }
        );
        
        // Step 2: Create team with question (only if question created successfully)
        if (questionRes.status === 200 || questionRes.status === 400) { // 400 = already exists, OK
            const teamPayload = JSON.stringify({ teamname, question_code });
            const teamRes = http.post(
                'http://localhost:8000/siamMPL/teamquestions/',
                teamPayload,
                { headers: { 'Content-Type': 'application/json' } }
            );

            // ✅ Update custom counters based on response
            if (teamRes.status === 200) teamCreatedSuccess.add(1);
            if (teamRes.status === 400) {
                const body = teamRes.body;
                if (body.includes('already allocated')) {
                    teamAlreadyExists.add(1);
                } else if (body.includes('alloted already')) {
                    questionAlreadyAllotted.add(1);
                }
            }
            if (teamRes.status === 404) questionNotFound.add(1);

            // Realistic performance checks based on load
            check(teamRes, {
                'System responded (any valid status)': (r) => r.status >= 200 && r.status < 500,
                'Team creation successful': (r) => r.status === 200,
                'No server errors (5xx)': (r) => r.status < 500,
                'Response under 10s (high load)': (r) => r.timings.duration < 10000,
                'Response under 5s (good)': (r) => r.timings.duration < 5000,
                'Response under 2s (excellent)': (r) => r.timings.duration < 2000,
            });
        }
    });
}

