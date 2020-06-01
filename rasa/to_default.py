import os


config= 'language: zh\n' \
        'pipeline:\n' \
        '  - name: JiebaTokenizer\n' \
        '  - name: RegexFeaturizer\n' \
        '  - name: EntitySynonymMapper\n' \
        '  - name: CRFEntityExtractor\n' \
        '  - name: LexicalSyntacticFeaturizer\n' \
        '  - name: CountVectorsFeaturize\n' \
        '  - name: CountVectorsFeaturizer\n' \
        '    analyzer: \"char_wb\"\n' \
        '    min_ngram: 1\n' \
        '    max_ngram: 4\n' \
        '  - name: DIETClassifier\n' \
        '    entity_recognition: False\n' \
        '    epochs: 100\n' \
        '  - name: ResponseSelector\n' \
        '    epochs: 100\n\n\n' \
        'policies:\n' \
        '  - name: MemoizationPolicy\n' \
        '  - name: TEDPolicy\n' \
        '    max_history: 5\n' \
        '    epochs: 100\n' \
        '  - name: MappingPolicy\n' \
        '  - name: FormPolicy\n'

credentials = 'rest:\n\n\n\n' \
              'socketio:\n' \
              ' user_message_evt: user_uttered\n' \
              ' bot_message_evt: bot_uttered\n' \
              ' session_persistence: true\n\n\n' \
              'rasa:\n' \
              '  url: \"http://localhost:5002/api\"\n'

endpoints = 'action_endpoint:\n' \
            ' url: \"http://localhost:5055/webhook\"\n'


def to_default(path):
    config_path = os.path.join(path, 'config.yml')
    credentials_path = os.path.join(path, 'credentials.yml')
    endpoints_path = os.path.join(path, 'endpoints.yml')
    with open(config_path, 'w', encoding='utf8') as f1:
        f1.write(config)
    with open(credentials_path, 'w', encoding='utf8') as f2:
        f2.write(credentials)
    with open(endpoints_path, 'w', encoding='utf8') as f3:
        f3.write(endpoints)


def to_endpoints(enps, path):
    endpoints_path = os.path.join(path, 'endpoints.yml')
    with open(endpoints_path, 'w', encoding='utf8') as f3:
        f3.write(enps)

