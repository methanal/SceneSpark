import React, { useState } from 'react';
import { Layout, message } from 'antd';
import { v4 as uuidv4 } from 'uuid';
import TextAreaUpload from './components/TextAreaUpload';
import VideoTabs from './components/VideoTabs';

const { Content, Footer, Header } = Layout;

const App = () => {
  const [videoClips, setVideoClips] = useState([]);
  const [videoClips2, setVideoClips2] = useState([]);
  const [selectedClip, setSelectedClip] = useState(null);
  const uniqueID = uuidv4();

  const pollExtract = async (uniqueID) => {
    const timeout = 1800000; // 总超时时间 30 分钟
    const pollInterval = 4000; // 每5秒轮询一次
    const endTime = Date.now() + timeout;

    const poll = async (resolve, reject) => {
      try {
        const extractResponse = await fetch(`/api/v1/extract/${uniqueID}`);
        if (extractResponse.ok) {
          const extractResult = await extractResponse.json();

          if (extractResult.msg === 'done') {
            if (extractResult.llm_srts && extractResult.llm_srts.length > 0) {
              setVideoClips(extractResult.llm_srts.map(item => ({
                ...item,
                url: item.file_path,
                tags: item.tags || [],
                description: item.description || '',
              })));
            }

            if (extractResult.imgs_info && extractResult.imgs_info.length > 0) {
              setVideoClips2(extractResult.imgs_info.map(item => ({
                ...item,
                url: item.file_path,
                tags: item.tags || [],
                description: item.description || '',
              })));
            }

            setVideoClips(extractResult.llm_srts.map(item => ({
              ...item,
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

  const handleClipClick = (clip) => {
    setSelectedClip(clip);
  };

  const handleUploadSuccess = async (uniqueID) => {
    await pollExtract(uniqueID);
  };

  return (
    <Layout>
      <Header>
        <h1 style={{ color: 'white' }}>SceneSpark</h1>h1>
      </Header>
      <Content style={{ padding: '20px' }}>
        <TextAreaUpload uniqueID={uniqueID}
          onUploadSuccess={handleUploadSuccess}
        />
        <VideoTabs
          videoClips={videoClips}
          videoClips2={videoClips2}
          onClipClick={handleClipClick}
          selectedClip={selectedClip}
        />
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        SceneSpark ©2024 Created by methanal
      </Footer>
    </Layout>
  );
};

export default App;
