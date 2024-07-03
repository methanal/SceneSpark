import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Input, Button, Upload, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

const { TextArea } = Input;

const TextAreaUpload = ({ uniqueID, onUploadSuccess }) => {
  const [text1, setText1] = useState('');
  const [text2, setText2] = useState('');

  const fetchPrompts = async (uniqueID) => {
    try {
      const response = await fetch(`/api/v1/prompts/${uniqueID}`);
      if (response.ok) {
        const result = await response.json();
        setText1(result.prompt1);
        setText2(result.prompt2);
      } else {
        message.error('Failed to fetch prompts');
      }
    } catch (error) {
      console.error('Fetch prompts error:', error);
      message.error('Failed to fetch prompts');
    }
  };

  const handleUpload = async (options) => {
    const { file, onSuccess, onError } = options;
    const formData = new FormData();
    formData.append('files', file);
    formData.append('prompt1', text1);
    formData.append('prompt2', text2);
    formData.append('request_id', uniqueID);

    try {
      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        body: formData,
      });

      console.log('Response status:', response.status);

      if (response.ok || response.status === 202) {
        await onUploadSuccess(uniqueID);
        onSuccess("ok");
      } else {
        onError('上传失败');
        message.error('上传失败1');
      }
    } catch (error) {
      onError(error);
      message.error('上传失败2');
    }
  };

  useEffect(() => {
    fetchPrompts(uniqueID);
  }, [uniqueID]);

  return (
    <>
      <Row gutter={16} style={{ marginBottom: '16px' }}>
        <Col span={12}>
          <Card title="Prompt 1">
            <TextArea
              value={text1}
              onChange={(e) => setText1(e.target.value)}
              placeholder="Input text here..."
              autoSize={{ minRows: 4, maxRows: 10 }}
              style={{ width: '100%' }}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Prompt 2">
            <TextArea
              value={text2}
              onChange={(e) => setText2(e.target.value)}
              placeholder="Input text here..."
              autoSize={{ minRows: 4, maxRows: 10 }}
              style={{ width: '100%' }}
            />
          </Card>
        </Col>
      </Row>
      <Row gutter={16} style={{ marginBottom: '16px' }}>
        <Col span={24}>
          <Upload
            accept="video/*"
            customRequest={handleUpload}
            multiple
          >
            <Button icon={<UploadOutlined />}>Upload Video</Button>
          </Upload>
        </Col>
      </Row>
    </>
  );
};

export default TextAreaUpload;
