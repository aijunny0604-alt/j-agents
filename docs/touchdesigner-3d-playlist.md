# 터치디자이너로 3D 플레이리스트 만들기

원본 로고·커버·음원으로 입체 크롬 로고, 반복 카메라, 물 반사와 실제 재생 UI가 있는 플레이리스트를 만드는 제작 규칙이다. BURNWAY 작업에서 확인한 개선 과정과 검증 기준을 포함한다.

- [제작 과정 및 작업 규칙 전체 문서](../skills/touchdesigner-3d-playlist/references/production-guide.md)
- [TouchDesigner 구현 기록](../skills/touchdesigner-3d-playlist/references/touchdesigner-notes.md)
- [Codex 스킬](../skills/touchdesigner-3d-playlist/SKILL.md)
- [Codex 전용 에이전트](../codex/agents/touchdesigner_playlist.toml)

## 개인 등록

`skills/touchdesigner-3d-playlist` 폴더 전체를 `~/.codex/skills/`에 복사한다. `codex/agents/touchdesigner_playlist.toml`을 `~/.codex/agents/`에 복사한다. `CODEX_HOME`을 별도로 설정한 경우 해당 디렉터리를 사용한다. 기존 같은 이름의 파일이 있다면 내용을 먼저 비교한다.

이 에이전트는 Codex의 독립 TOML 형식이다. 기존 Claude Code 플러그인의 에이전트 수나 설치 흐름을 바꾸지 않는다. 모델·추론 강도·권한은 호출 환경에서 상속한다. 새 작업에서 스킬 또는 에이전트가 발견되는지 확인한다.

호출 예:

```text
$touchdesigner-3d-playlist 제공한 로고, 커버와 WAV 7곡으로 입체 크롬 플레이리스트를 만들어줘.
```

```text
touchdesigner_playlist 에이전트를 사용해 이 프로젝트의 크롬 로고와 반복 모션을 제작해줘.
```

등록 형식 참고: [OpenAI 공식 커스텀 에이전트 문서](https://learn.chatgpt.com/docs/agent-configuration/subagents).

원본 음악·이미지·영상은 이 문서 패키지에 포함하지 않는다. 실제 제작 시 해당 작업의 입력 파일을 제공한다.
