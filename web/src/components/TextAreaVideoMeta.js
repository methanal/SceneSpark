import React, { useState, useEffect } from 'react';
import { Card, Col, Button, Divider, Input, message, Row, Select } from 'antd';

const { TextArea } = Input;
const { Option } = Select;

const TextAreaVideoMeta = ({ uniqueID, handleFetchTab5 }) => {
  const [text4, setText4] = useState('');
  const [text5, setText5] = useState('');
  const [text6, setText6] = useState('');
  const [translationModel, setTranslationModel] = useState('whisper');
  const [modelSize, setModelSize] = useState('small');
  const [samplingInterval, setSamplingInterval] = useState(2);
  const [clipDuration, setClipDuration] = useState(2);
  const modelSizeOptions = translationModel === 'whisper' ? ['small', 'medium'] : [];

  const fetchPrompts = async (uniqueID) => {
    try {
      const response = await fetch(`/api/v1/prompts/${uniqueID}`);
      if (response.ok) {
        const result = await response.json();
        setText4(result.img_meta_desc_subs || '');
        setText5(result.img_meta_tag_score || '');
        setText6(result.video_meta_prompt || '');
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
      <Row gutter={16} style={{ marginTop: '16px', marginBottom: '16px' }}>
        <Col span={24}>
          <Card size="small" title="Step1, Extract description & subtitle from Video Frames">
            <TextArea
              value={text4}
              onChange={(e) => setText4(e.target.value)}
              placeholder="Input Prompt here..."
              autoSize={{ minRows: 10, maxRows: 14 }}
              style={{ width: '100%' }}
            />
          </Card>
        </Col>
      </Row>
      <Row gutter={16} style={{ marginTop: '16px', marginBottom: '16px' }}>
        <Col span={24}>
          <Card size="small" title="Step2, Extract tags & score from Video Frames">
            <TextArea
              value={text5}
              onChange={(e) => setText5(e.target.value)}
              placeholder="Input Prompt here..."
              autoSize={{ minRows: 10, maxRows: 14 }}
              style={{ width: '100%' }}
            />
          </Card>
        </Col>
      </Row>
      <Row gutter={16} style={{ marginTop: '16px', marginBottom: '16px' }}>
        <Col span={24}>
          <Card size="small" title="Step3, Pick clips from Video Meta">
            <TextArea
              value={text6}
              onChange={(e) => setText6(e.target.value)}
              placeholder="Input Prompt here..."
              autoSize={{ minRows: 10, maxRows: 14 }}
              style={{ width: '100%' }}
            />
          </Card>
        </Col>
      </Row>
      <Button onClick={() => handleFetchTab5(translationModel, modelSize, samplingInterval, clipDuration, text4, text5, text6)} style={{ marginTop: '16px' }}>Extract Clips</Button>
    </>
  );
};

export default TextAreaVideoMeta;
