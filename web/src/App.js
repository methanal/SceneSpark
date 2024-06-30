import React, { useState } from 'react';
import { Upload, Button, Layout, Tag, Descriptions, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import ReactPlayer from 'react-player';
import VideoClipList from './components/VideoClipList';
import { v4 as uuidv4 } from 'uuid';

const { Content, Footer, Header } = Layout;

const App = () => {
  const [videoClips, setVideoClips] = useState([]);
  const [selectedClip, setSelectedClip] = useState(null);

  const pollExtract = async (uniqueID) => {
    const timeout = 1800000; // 总超时时间 30 分钟
    const pollInterval = 4000; // 每5秒轮询一次
    const endTime = Date.now() + timeout;

    const poll = async (resolve, reject) => {
      try {
        const extractResponse = await fetch(`http://127.0.0.1:8000/api/v1/extract/${uniqueID}`);
        if (extractResponse.ok) {
          const extractResult = await extractResponse.json();

          if (extractResult.msg === 'done' && extractResult.llm_srts && extractResult.llm_srts.length > 0) {
            setVideoClips(extractResult.llm_srts.map(item => ({
              url: item.file_path,
              tags: item.tags || [],
              description: item.description || ''
            })));
            message.info('Extraction completed successfully.');
            return resolve();
          } else if (Date.now() >= endTime) {
            message.error('Polling timed out.');
            return reject(new Error('Polling timed out.'));
          }
        } else {
          message.error('Extraction failed');
          return reject(new Error('Extraction failed'));
        }
      } catch (error) {
        console.error('Polling error:', error);
        return reject(error);
      }

      setTimeout(() => poll(resolve, reject), pollInterval);
    };

    return new Promise(poll);
  };
  const handleUpload = async (options) => {
    const { file, onSuccess, onError } = options;
    const formData = new FormData();
    formData.append('files', file);

    const uniqueID = uuidv4();
    formData.append('request_id', uniqueID);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/upload', {
        method: 'POST',
        body: formData
      });

      console.log('Response status:', response.status);

      if (response.ok || response.status === 202) {
        await pollExtract(uniqueID);
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

  const handleClipClick = (clip) => {
    setSelectedClip(clip);
  };

  return (
    <Layout>
      <Header>
        <Upload
          accept="video/*"
          customRequest={handleUpload}
          multiple
        >
          <Button icon={<UploadOutlined />}>Upload Video</Button>
        </Upload>
      </Header>
      <Content style={{ padding: '20px' }}>
        <VideoClipList videoClips={videoClips} onClipClick={handleClipClick} />
        {selectedClip && (
          <div style={{ marginTop: '20px' }}>
            <ReactPlayer url={selectedClip.url} controls />
            <Descriptions title="Video Clip Details" bordered>
              <Descriptions.Item label="Description">{selectedClip.description}</Descriptions.Item>
              <Descriptions.Item label="Tags">
                {selectedClip.tags.map(tag => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        SceneSpark ©2024 Created by methanal
      </Footer>
    </Layout>
  );
};

export default App;
