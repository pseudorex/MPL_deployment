import http from 'k6/http';
import { check } from 'k6';
import { Counter, Rate } from 'k6/metrics';

// ✅ System-wide metrics
const totalOperations = new Counter('total_operations');
const successfulOperations = new Counter('successful_operations');
const systemUptime = new Rate('system_uptime');
const fastOperations = new Rate('fast_operations_under_3s');

function simpleUuid() {
    return Math.random().toString(36).substring(2, 8);
}

export const options = {
    vus: 150,           // 150 concurrent users
    duration: '30s',    // Run for exactly 30 seconds
};

export default function () {
    const uniqueId = simpleUuid();
    
    // Complete user journey simulation
    const scenarios = [
        () => teamWorkflow(uniqueId),
        () => mysteryWorkflow(uniqueId),
        () => adminWorkflow(uniqueId),
        () => mixedWorkflow(uniqueId)
    ];
    
    const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
    scenario();
}

function teamWorkflow(uniqueId) {
    const teamname = `SystemTest_${uniqueId}`;
    const question_code = `ST_Q_${uniqueId}`;
    
    totalOperations.add(1);
    
    // Create question
    const questionRes = http.post(
        'http://localhost:8000/siamMPL/admin/questions/',
        JSON.stringify({ id: question_code, question: `System test ${uniqueId}` }),
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    if (questionRes.status === 200 || questionRes.status === 400) {
        // Create team
        const teamRes = http.post(
            'http://localhost:8000/siamMPL/teamquestions/',
            JSON.stringify({ teamname, question_code }),
            { headers: { 'Content-Type': 'application/json' } }
        );
        
        check(teamRes, {
            '✅ Team workflow successful': (r) => r.status === 200 || r.status === 400,
            '⚡ Fast workflow (<3s)': (r) => r.timings.duration < 3000,
        });
        
        if (teamRes.status === 200) successfulOperations.add(1);
        systemUptime.add(teamRes.status < 500 ? 1 : 0);
        fastOperations.add(teamRes.timings.duration < 3000 ? 1 : 0);
    }
}

function mysteryWorkflow(uniqueId) {
    const teamname = `MysteryTest_${uniqueId}`;
    const question_code = `MT_Q_${uniqueId}`;
    
    totalOperations.add(1);
    
    // Quick setup
    http.post(
        'http://localhost:8000/siamMPL/admin/questions/',
        JSON.stringify({ id: question_code, question: `Mystery setup ${uniqueId}` }),
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    const teamRes = http.post(
        'http://localhost:8000/siamMPL/teamquestions/',
        JSON.stringify({ teamname, question_code }),
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    if (teamRes.status === 200) {
        // Assign mystery
        const difficulties = ['easy', 'medium', 'hard'];
        const mysteryRes = http.put(
            'http://localhost:8000/siamMPL/mystery/',
            JSON.stringify({
                team_name: teamname,
                difficulty: difficulties[Math.floor(Math.random() * difficulties.length)],
                cost: 50
            }),
            { headers: { 'Content-Type': 'application/json' } }
        );
        
        check(mysteryRes, {
            '✅ Mystery workflow works': (r) => r.status === 200 || r.status === 400 || r.status === 404,
            '⚡ Fast mystery (<4s)': (r) => r.timings.duration < 4000,
        });
        
        if (mysteryRes.status === 200) successfulOperations.add(1);
        systemUptime.add(mysteryRes.status < 500 ? 1 : 0);
        fastOperations.add(mysteryRes.timings.duration < 3000 ? 1 : 0);
    }
}

function adminWorkflow(uniqueId) {
    totalOperations.add(1);
    
    // Admin data retrieval
    const adminRes = http.get('http://localhost:8000/siamMPL/admin/teams/');
    
    check(adminRes, {
        '✅ Admin operations work': (r) => r.status === 200,
        '⚡ Fast admin query (<2s)': (r) => r.timings.duration < 2000,
    });
    
    if (adminRes.status === 200) successfulOperations.add(1);
    systemUptime.add(adminRes.status < 500 ? 1 : 0);
    fastOperations.add(adminRes.timings.duration < 3000 ? 1 : 0);
}

function mixedWorkflow(uniqueId) {
    totalOperations.add(1);
    
    // Mixed operations
    const operations = [
        () => http.get('http://localhost:8000/siamMPL/admin/questions/'),
        () => http.get('http://localhost:8000/siamMPL/admin/mystery-questions/'),
        () => http.post(
            'http://localhost:8000/siamMPL/admin/mystery-questions/',
            JSON.stringify({
                difficulty: 'medium',
                question: `Mixed test ${uniqueId}`,
                question_status: 'UNALLOCATED'
            }),
            { headers: { 'Content-Type': 'application/json' } }
        )
    ];
    
    const operation = operations[Math.floor(Math.random() * operations.length)];
    const res = operation();
    
    check(res, {
        '✅ Mixed operations successful': (r) => r.status === 200,
        '⚡ Fast mixed ops (<3s)': (r) => r.timings.duration < 3000,
    });
    
    if (res.status === 200) successfulOperations.add(1);
    systemUptime.add(res.status < 500 ? 1 : 0);
    fastOperations.add(res.timings.duration < 3000 ? 1 : 0);
}
