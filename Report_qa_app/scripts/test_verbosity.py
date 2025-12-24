from rules_engine.rules_loader import load_rules
from rules_engine.engine import evaluate

cfg = load_rules('config/rules_en.yml')
# enable representative checks
cfg['_enabled_checks'] = [
    'required_sections','first_person','forbidden_phrases','subjective_language',
    'bias_language','vagueness','repetition','passive_voice_ratio','missing_image_caption'
]
text = "This sample report text includes the phrase we believe and mentions Figure 1 but omits many section headings."
meta = {'filename':'test.docx','language':'English','paragraphs':[]}

for v in (30, 60, 90):
    cfg['_verbosity'] = v
    issues = evaluate(text, meta, cfg)
    print(f"verbosity={v} -> {len(issues)} issues")
    for iss in issues[:5]:
        print(' ', iss.get('rule_id'), iss.get('severity'))
    print()
