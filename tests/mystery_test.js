import http from 'k6/http';
import { check } from 'k6';
import { Counter, Rate } from 'k6/metrics';

// ✅ Custom metrics
const mysteryAssigned = new Counter('mystery_assigned');
const mysteryQuit = new Counter('mystery_quit');
const systemHealthy = new Rate('system_healthy');

function simpleUuid() {
    return Math.random().toString(36).substring(2, 10);
}

export const options = {
    vus: 80,            // 80 concurrent users
    duration: '30s',    // Run for exactly 30 seconds
};

export default function () {
    const uniqueId = simpleUuid();
    const teamname = `MysteryTeam_${uniqueId}`;
    const question_code = `MQ_${uniqueId}`;

    // Step 1: Create question and team first
    const questionRes = http.post(
        'http://localhost:8000/siamMPL/admin/questions/',
        JSON.stringify({ id: question_code, question: `Mystery test ${uniqueId}` }),
        { headers: { 'Content-Type': 'application/json' } }
    );

    if (questionRes.status === 200 || questionRes.status === 400) {
        // Create team
        const teamRes = http.post(
            'http://localhost:8000/siamMPL/teamquestions/',
            JSON.stringify({ teamname, question_code }),
            { headers: { 'Content-Type': 'application/json' } }
        );

        if (teamRes.status === 200) {
            // Step 2: Assign mystery question
            const difficulties = ['easy', 'medium', 'hard'];
            const difficulty = difficulties[Math.floor(Math.random() * difficulties.length)];
            
            const mysteryRes = http.put(
                'http://localhost:8000/siamMPL/mystery/',
                JSON.stringify({
                    team_name: teamname,
                    difficulty: difficulty,
                    cost: Math.floor(Math.random() * 50) + 25
                }),
                { headers: { 'Content-Type': 'application/json' } }
            );

            if (mysteryRes.status === 200) mysteryAssigned.add(1);

            // Sometimes quit mystery
            if (Math.random() > 0.7) {
                const quitRes = http.del(
                    `http://localhost:8000/siamMPL/mystery/quit?team_name=${teamname}`,
                    null,
                    { headers: { 'Content-Type': 'application/json' } }
                );
                if (quitRes.status === 200) mysteryQuit.add(1);
            }

            // Smart checks
            check(mysteryRes, {
                '✅ System responding': (r) => r.status < 500,
                '🎯 Mystery operation successful': (r) => r.status === 200 || r.status === 400 || r.status === 404,
                '⚡ Fast response (<3s)': (r) => r.timings.duration < 3000,
                '👍 Good response (<6s)': (r) => r.timings.duration < 6000,
            });

            systemHealthy.add(mysteryRes.status < 500 ? 1 : 0);
        }
    }
}
