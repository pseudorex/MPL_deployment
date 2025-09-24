import http from 'k6/http';
import { check, group } from 'k6';
import { Counter } from 'k6/metrics';
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.3.0/index.js';

// ✅ Custom metrics
const createdCount = new Counter('team_created_success');
const alreadyAllottedCount = new Counter('question_already_allotted');

export const options = {
    vus: 100,
    iterations: 200
};

export default function () {
    group('Team-Question Concurrency Test', function () {
        const teamname = `ConcurrentTeam_${uuidv4()}`;
        const question_code = 'Q123'; // Make sure this exists in your DB

        const payload = JSON.stringify({ teamname, question_code });
        const res = http.post(
            'http://localhost:8000/siamMPL/teamquestions/',
            payload,
            { headers: { 'Content-Type': 'application/json' } }
        );

        // ✅ Update custom counters
        if (res.status === 200) createdCount.add(1);
        if (res.status === 400) alreadyAllottedCount.add(1);

        // Check response and log in terminal
        check(res, {
            'Created successfully → 200': (r) => r.status === 200,
            'Question already allotted → 400': (r) => r.status === 400
        });
    });
}
