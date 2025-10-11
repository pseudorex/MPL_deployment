import http from 'k6/http';
import { check } from 'k6';
import { Counter, Rate } from 'k6/metrics';

// ✅ Custom metrics
const adminOperationsSuccess = new Counter('admin_operations_success');
const dataRetrieved = new Counter('data_retrieved');
const systemHealthy = new Rate('system_healthy');

function simpleUuid() {
    return Math.random().toString(36).substring(2, 10);
}

export const options = {
    vus: 60,            // 60 concurrent users
    duration: '30s',    // Run for exactly 30 seconds
};

export default function () {
    const uniqueId = simpleUuid();
    
    // Random admin operation selection
    const operations = [
        () => testGetTeams(),
        () => testGetQuestions(),
        () => testGetMysteries(),
        () => testCreateQuestion(uniqueId),
        () => testCreateMystery(uniqueId),
        () => testUpdateTeam(uniqueId)
    ];
    
    const operation = operations[Math.floor(Math.random() * operations.length)];
    operation();
}

function testGetTeams() {
    const res = http.get('http://localhost:8000/siamMPL/admin/teams/');
    
    check(res, {
        '✅ Teams retrieved': (r) => r.status === 200,
        '⚡ Fast response (<2s)': (r) => r.timings.duration < 2000,
    });
    
    if (res.status === 200) {
        adminOperationsSuccess.add(1);
        dataRetrieved.add(1);
    }
    systemHealthy.add(res.status < 500 ? 1 : 0);
}

function testGetQuestions() {
    const res = http.get('http://localhost:8000/siamMPL/admin/questions/');
    
    check(res, {
        '✅ Questions retrieved': (r) => r.status === 200,
        '⚡ Fast response (<2s)': (r) => r.timings.duration < 2000,
    });
    
    if (res.status === 200) {
        adminOperationsSuccess.add(1);
        dataRetrieved.add(1);
    }
    systemHealthy.add(res.status < 500 ? 1 : 0);
}

function testGetMysteries() {
    const res = http.get('http://localhost:8000/siamMPL/admin/mystery-questions/');
    
    check(res, {
        '✅ Mysteries retrieved': (r) => r.status === 200,
        '⚡ Fast response (<2s)': (r) => r.timings.duration < 2000,
    });
    
    if (res.status === 200) {
        adminOperationsSuccess.add(1);
        dataRetrieved.add(1);
    }
    systemHealthy.add(res.status < 500 ? 1 : 0);
}

function testCreateQuestion(uniqueId) {
    const res = http.post(
        'http://localhost:8000/siamMPL/admin/questions/',
        JSON.stringify({
            id: `ADMIN_Q_${uniqueId}`,
            question: `Admin test question ${uniqueId}`
        }),
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    check(res, {
        '✅ Question created/exists': (r) => r.status === 200 || r.status === 400,
        '👍 Good response (<4s)': (r) => r.timings.duration < 4000,
    });
    
    if (res.status === 200 || res.status === 400) adminOperationsSuccess.add(1);
    systemHealthy.add(res.status < 500 ? 1 : 0);
}

function testCreateMystery(uniqueId) {
    const difficulties = ['easy', 'medium', 'hard'];
    const res = http.post(
        'http://localhost:8000/siamMPL/admin/mystery-questions/',
        JSON.stringify({
            difficulty: difficulties[Math.floor(Math.random() * difficulties.length)],
            question: `Admin mystery ${uniqueId}`,
            question_status: 'UNALLOCATED'
        }),
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    check(res, {
        '✅ Mystery created': (r) => r.status === 200,
        '👍 Good response (<4s)': (r) => r.timings.duration < 4000,
    });
    
    if (res.status === 200) adminOperationsSuccess.add(1);
    systemHealthy.add(res.status < 500 ? 1 : 0);
}

function testUpdateTeam(uniqueId) {
    // First create a team to update
    const teamName = `AdminTestTeam_${uniqueId}`;
    const questionId = `ADMIN_UPD_Q_${uniqueId}`;
    
    // Create question
    http.post(
        'http://localhost:8000/siamMPL/admin/questions/',
        JSON.stringify({ id: questionId, question: `Update test ${uniqueId}` }),
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    // Create team
    const teamCreateRes = http.post(
        'http://localhost:8000/siamMPL/teamquestions/',
        JSON.stringify({ teamname: teamName, question_code: questionId }),
        { headers: { 'Content-Type': 'application/json' } }
    );
    
    if (teamCreateRes.status === 200) {
        // Update team points
        const res = http.put(
            `http://localhost:8000/siamMPL/admin/teams/${teamName}`,
            JSON.stringify({ points: Math.floor(Math.random() * 500) + 100 }),
            { headers: { 'Content-Type': 'application/json' } }
        );
        
        check(res, {
            '✅ Team updated': (r) => r.status === 200,
            '👍 Good response (<4s)': (r) => r.timings.duration < 4000,
        });
        
        if (res.status === 200) adminOperationsSuccess.add(1);
        systemHealthy.add(res.status < 500 ? 1 : 0);
    }
}
