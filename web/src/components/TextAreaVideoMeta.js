import React, { useState, useEffect } from 'react';
import { Card, Col, Button, Divider, Input, message, Row, Select } from 'antd';

const { TextArea } = Input;
const { Option } = Select;

const TextAreaVideoMeta = ({ uniqueID, handleFetchTab5 }) => {
  const [text4, setText4] = useState('');
  const [translationModel, setTranslationModel] = useState('whisper');
  const [modelSize, setModelSize] = useState('small');
  const [whisper_prompt, setText_prompt] = useState('');
  const [samplingInterval, setSamplingInterval] = useState(3);
  const [clipDuration, setClipDuration] = useState(3);
  const modelSizeOptions = translationModel === 'whisper' ? ['small', 'medium'] : [];

  const fetchPrompts = async (uniqueID) => {
    try {
      const response = await fetch(`/api/v1/prompts/${uniqueID}`);
      if (response.ok) {
        const result = await response.json();
        setText4(result.video_meta_prompt || '');
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
      <Row gutter={16} style={{ marginTop: '16px', marginBottom: '16px' }}>
        <Col span={12}>
          <Card size="small" title="Audeo Settings">
           <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
             <span style={{ marginLeft: '10px', marginRight: '10px' }}>Translation Model</span>
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
               style={{ width: '100px', marginRight: '8px' }}
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
          </Card>
        </Col>
        <Col span={12}>
          <Card size="small" title="Video Settings">
            <span style={{ marginLeft: '10px', marginRight: '8px' }}>Sample Interval</span>
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
          </Card>
        </Col>
      </Row>
      <TextArea
        value={text4}
        onChange={(e) => setText4(e.target.value)}
        placeholder="Input Prompt here..."
        autoSize={{ minRows: 10, maxRows: 14 }}
        style={{ width: '100%' }}
      />
      <Button onClick={() => handleFetchTab5(translationModel, modelSize, whisper_prompt, samplingInterval, clipDuration, text4)} style={{ marginTop: '16px' }}>Extract Clips</Button>
    </>
  );
};

export default TextAreaVideoMeta;
