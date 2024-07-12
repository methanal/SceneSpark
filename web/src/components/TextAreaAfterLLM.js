import React, { useState, useEffect } from 'react';
import { Divider, Row, Col, Card, Input, Button, message, Select } from 'antd';

const { TextArea } = Input;
const { Option } = Select;

const TextAreaAfterLLM = ({ uniqueID, handleFetchTab1, handleFetchTab2 }) => {
  const [text1, setText1] = useState('');
  const [text2, setText2] = useState('');
  const [whisper_prompt, setText_prompt] = useState('');
  const [samplingInterval, setSamplingInterval] = useState(3);
  const [clipDuration, setClipDuration] = useState(3);
  const [translationModel, setTranslationModel] = useState('whisper');
  const [modelSize, setModelSize] = useState('small');
  const modelSizeOptions = translationModel === 'whisper' ? ['small', 'medium'] : [];

  const fetchPrompts = async (uniqueID) => {
    try {
      const response = await fetch(`/api/v1/prompts/${uniqueID}`);
      if (response.ok) {
        const result = await response.json();
        setText1(result.subtitle_prompt || '');
        setText2(result.vision_prompt || '');
        setText_prompt(result.whisper_prompt || '');
      } else {
        message.error('Failed to fetch prompts');
      }
    } catch (error) {
      console.error('Fetch prompts error:', error);
      message.error('Failed to fetch prompts');
    }
  };

  useEffect(() => {
    fetchPrompts(uniqueID);
  }, [uniqueID]);

  return (
    <>
      <Row gutter={16} style={{ marginBottom: '16px' }}>
        <Col span={12}>
          <Card size="small" title="Subtitle Prompt">
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
              <span style={{ marginRight: '10px' }}>Translation Model</span>
              <Select
                value={translationModel}
                onChange={setTranslationModel}
                style={{ width: '220px', marginRight: '16px' }}
              >
                <Option value="whisper">whisper</Option>
                <Option value="openai" disabled>Whisper API (large-v2)</Option>Option>
                <Option value="faster">faster-whisper (CTranslate2)</Option>Option>
                <Option value="sense_voice" disabled>SenseVoice</Option>Option>
              </Select>
              <Divider type="vertical"/>
              <span style={{ marginRight: '10px' }}>Model Size</span>
              <Select
                value={modelSize}
                onChange={setModelSize}
                style={{ width: '100px' }}
                disabled={modelSizeOptions.length === 0}
              >
                {modelSizeOptions.length > 0 ? (
                  modelSizeOptions.map(size => (
                    <Option key={size} value={size}>
                      {size}
                    </Option>
                  ))
                ) : (
                  <Option value="" disabled>
                    No options
                  </Option>
                )}
              </Select>
            </div>
            <TextArea
              value={whisper_prompt}
              onChange={(e) => setText_prompt(e.target.value)}
              placeholder="Input Whisper Prompt here..."
              autoSize={{ minRows: 4, maxRows: 10 }}
              style={{ width: '100%' }}
            />
            <Divider />
            <TextArea
              value={text1}
              onChange={(e) => setText1(e.target.value)}
              placeholder="Input Prompt here..."
              autoSize={{ minRows: 10, maxRows: 14 }}
              style={{ width: '100%' }}
            />
            <Button onClick={() => handleFetchTab1(text1, translationModel, modelSize, whisper_prompt)} style={{ marginTop: '16px' }}>Extract Clips</Button>
          </Card>
        </Col>
        <Col span={12}>
          <Card size="small" title="LLM Vision Prompt">
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
              <span style={{ marginRight: '8px' }}>Sample Interval</span>
              <Input
                type="number"
                value={samplingInterval}
                onChange={(e) => setSamplingInterval(Number(e.target.value))}
                placeholder="Enter sampling interval"
                style={{ width: '60px', marginRight: '8px' }}
              />
              <span style={{ marginRight: '8px' }}>seconds</span>
              <Divider type="vertical"/>
              <span style={{ marginRight: '8px' }}>Clip Duration</span>
              <Input
                type="number"
                value={clipDuration}
                onChange={(e) => setClipDuration(Number(e.target.value))}
                placeholder="Enter clip duration"
                style={{ width: '60px', marginRight: '8px' }}
              />
              <span>seconds</span>
            </div>
            <TextArea
              value={text2}
              onChange={(e) => setText2(e.target.value)}
              placeholder="Input text here..."
              autoSize={{ minRows: 10, maxRows: 20 }}
              style={{ width: '100%' }}
            />
            <Button onClick={() => handleFetchTab2(text2, samplingInterval, clipDuration)} style={{ marginTop: '16px' }}>Extract Clips</Button>
          </Card>
        </Col>
      </Row>
    </>
  );
};

export default TextAreaAfterLLM;