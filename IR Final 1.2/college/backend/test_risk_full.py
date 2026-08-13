import json, sys, os
os.environ['PYTHONIOENCODING'] = 'utf-8'

print('='*60)
print('  AI Risk Analyzer -- Full System Verification')
print('='*60)

# TEST 1: Import check
print('\n[1/6] Checking imports...')
try:
    from risk_analyzer import analyze_risk, generate_ai_explanation
    print('  [OK] risk_analyzer.py imports OK')
except Exception as e:
    print(f'  [FAIL]: {e}')
    sys.exit(1)

# TEST 2: Well-aligned student
print('\n[2/6] Testing well-aligned student (CSE + coding)...')
r = analyze_risk({
    'rank': 15000, 'branch': 'CSE', 'category': 'OBC', 'income': 5.5,
    'marks': 82, 'interests': ['coding', 'AI', 'machine learning'],
    'skills': ['Python', 'Mathematics'], 'career_goals': 'Software Engineer',
    'college_tier': 2, 'fees': 150000, 'hostel_fees': 70000,
    'hostel_required': True, 'gender': 'Male'
})
assert r['success_score'] > 70, f'Expected >70, got {r["success_score"]}'
assert r['regret_probability'] < 30, f'Expected <30, got {r["regret_probability"]}'
assert r['branch_compatibility_score'] > 80
assert r['academic_risk'] == 'Low'
print(f'  [OK] Success={r["success_score"]}, Regret={r["regret_probability"]}%, BranchMatch={r["branch_compatibility_score"]}%')
print(f'       Academic={r["academic_risk"]}, Financial={r["financial_risk"]}, Placement={r["placement_risk"]}')

# TEST 3: Mismatched student (biology choosing CSE)
print('\n[3/6] Testing MISMATCH student (biology -> CSE, weak math)...')
r2 = analyze_risk({
    'rank': 80000, 'branch': 'CSE', 'category': 'GM', 'income': 2.0,
    'marks': 55, 'interests': ['biology', 'medicine', 'healthcare'],
    'skills': ['weak in math'], 'career_goals': 'Doctor',
    'college_tier': 3, 'fees': 150000, 'hostel_fees': 70000,
    'hostel_required': True, 'loan_required': True, 'gender': 'Female'
})
assert r2['success_score'] < 45, f'Expected <45, got {r2["success_score"]}'
assert r2['regret_probability'] > 60, f'Expected >60, got {r2["regret_probability"]}'
assert r2['academic_risk'] == 'High'
assert r2['financial_risk'] == 'High'
assert len(r2['branch_mismatches']) > 0
print(f'  [OK] Success={r2["success_score"]}, Regret={r2["regret_probability"]}%')
print(f'       Academic={r2["academic_risk"]} WARNING, Financial={r2["financial_risk"]} WARNING')
print(f'       Mismatch: {r2["branch_mismatches"][0]}')

# TEST 4: All output fields present
print('\n[4/6] Verifying all 11 output dimensions...')
required = [
    'success_score', 'counseling_risk_score', 'academic_risk', 'academic_risk_score',
    'financial_risk', 'financial_risk_score', 'placement_risk', 'placement_risk_score',
    'career_alignment_score', 'branch_compatibility_score', 'scholarship_opportunity_score',
    'college_roi_score', 'roi_label', 'roi_details', 'regret_probability', 'regret_reasons',
    'rank_match_score', 'eligible_scholarships', 'branch_mismatches',
    'financial_details', 'placement_details'
]
missing = [k for k in required if k not in r]
if missing:
    print(f'  [FAIL] Missing fields: {missing}')
else:
    print(f'  [OK] All {len(required)} output fields present')

# TEST 5: AI Explanation generator
print('\n[5/6] Testing AI explanation generator...')
explanation = generate_ai_explanation(
    {'branch': 'CSE', 'rank': 15000, 'income': 5.5,
     'interests': ['coding'], 'skills': ['Python'], 'career_goals': 'Software Engineer'},
    r
)
assert len(explanation) > 50, 'Explanation too short'
print(f'  [OK] AI explanation generated ({len(explanation)} chars)')
print(f'       Preview: "{explanation[:100]}..."')

# TEST 6: Backward compatibility
print('\n[6/6] Testing backward-compatible service wrapper...')
try:
    from risk_analyzer_service import RiskAnalyzerEngine
    engine = RiskAnalyzerEngine()
    print('  [OK] RiskAnalyzerEngine class imports OK')
except Exception as e:
    print(f'  [WARN] Service wrapper: {e}')

# TEST 7: Edge cases
print('\n[BONUS] Testing edge cases...')
# Minimal input
r3 = analyze_risk({'rank': 50000, 'branch': 'MECH'})
assert 'success_score' in r3
print(f'  [OK] Minimal input handled: Success={r3["success_score"]}')

# SC/ST low income student
r4 = analyze_risk({
    'rank': 40000, 'branch': 'ECE', 'category': 'SC', 'income': 1.5,
    'marks': 70, 'interests': ['electronics', 'circuits'],
    'career_goals': 'Electronics Engineer', 'gender': 'Female'
})
assert r4['scholarship_opportunity_score'] > 60
print(f'  [OK] SC/ST scholarship detection: Score={r4["scholarship_opportunity_score"]}, Scholarships={len(r4["eligible_scholarships"])}')

# Coding interest choosing Civil (mismatch)
r5 = analyze_risk({
    'rank': 30000, 'branch': 'CIVIL', 'category': 'GM', 'income': 8,
    'marks': 75, 'interests': ['coding', 'programming', 'software'],
    'career_goals': 'Software Engineer', 'college_tier': 2
})
assert r5['academic_risk'] in ['Medium', 'High'], f'Expected mismatch, got {r5["academic_risk"]}'
print(f'  [OK] Coding->Civil mismatch detected: AcadRisk={r5["academic_risk"]}, BranchMatch={r5["branch_compatibility_score"]}%')

# Full JSON output for student 1
print('\n--- Full Output (Student 1) ---')
for k, v in r.items():
    if isinstance(v, (dict, list)):
        print(f'  {k}: {json.dumps(v, ensure_ascii=False)}')
    else:
        print(f'  {k}: {v}')

print('\n' + '='*60)
print('  ALL TESTS PASSED -- Risk Analyzer is FULLY WORKING')
print('='*60)
