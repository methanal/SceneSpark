import React, { useState } from 'react';
import { Button, Divider, Tabs, Descriptions, Tag, Row, Col } from 'antd';
import ReactPlayer from 'react-player';
import VideoClipList from './VideoClipList';

const { TabPane } = Tabs;

const VideoTriTabs = ({ videoClips, videoClips2, videoClips3, handleFetchTab3 }) => {
  const [selectedClip1, setSelectedClip1] = useState(null);
  const [selectedClip2, setSelectedClip2] = useState(null);
  const [selectedClip3, setSelectedClip3] = useState(null);

  const handleClipClick1 = (clip) => {
    setSelectedClip1(clip);
  };

  const handleClipClick2 = (clip) => {
    setSelectedClip2(clip);
  };

  const handleClipClick3 = (clip) => {
    setSelectedClip3(clip);
  };

  return (
  <>
    <Row gutter={16}>
      <Col span={12}>
        <Tabs defaultActiveKey="1">
          <TabPane tab="Subtitle Clipper" key="1">
            <VideoClipList videoClips={videoClips} onClipClick={handleClipClick1} />
            {selectedClip1 && (
              <div style={{ marginTop: '20px' }}>
                <ReactPlayer url={selectedClip1.url} controls />
                <Descriptions title="Video Clip Details" bordered>
                  <Descriptions.Item label="Description">{selectedClip1.description}</Descriptions.Item>
                  <Descriptions.Item label="Tags">
                    {selectedClip1.tags.map(tag => (
                      <Tag key={tag}>{tag}</Tag>
                    ))}
                  </Descriptions.Item>
                  <Descriptions.Item label="JSON">
                    <pre>{JSON.stringify(selectedClip1, null, 2)}</pre>
                  </Descriptions.Item>
                </Descriptions>
              </div>
            )}
          </TabPane>
        </Tabs>
      </Col>
      <Col span={12}>
        <Tabs defaultActiveKey="1">
          <TabPane tab="LLM Vision Clipper" key="1">
            <VideoClipList videoClips={videoClips2} onClipClick={handleClipClick2} />
            {selectedClip2 && (
              <div style={{ marginTop: '20px' }}>
                <ReactPlayer url={selectedClip2.url} controls />
                <Descriptions title="Video Clip Details" bordered>
                  <Descriptions.Item label="Description">{selectedClip2.description}</Descriptions.Item>
                  <Descriptions.Item label="Tags">
                    {selectedClip2.tags.map(tag => (
                      <Tag key={tag}>{tag}</Tag>
                    ))}
                  </Descriptions.Item>
                  <Descriptions.Item label="JSON">
                    <pre>{JSON.stringify(selectedClip2, null, 2)}</pre>
                  </Descriptions.Item>
                </Descriptions>
              </div>
            )}
          </TabPane>
        </Tabs>
      </Col>
    </Row>
    <Divider />
    <Button onClick={() => handleFetchTab3()} style={{ marginTop: '16px' }}>Merge Timeline</Button>
    <Row gutter={16} style={{ marginBottom: '16px' }}>
      <Tabs defaultActiveKey="1">
        <TabPane tab="Clips" key="1">
          <VideoClipList videoClips={videoClips3} onClipClick={handleClipClick3} />
          {selectedClip3 && (
            <div style={{ marginTop: '20px' }}>
              <ReactPlayer url={selectedClip3.url} controls />
              <Descriptions title="Video Clip Details" bordered>
                <Descriptions.Item label="Description">{selectedClip3.description}</Descriptions.Item>
                <Descriptions.Item label="Tags">
                  {selectedClip3.tags.map(tag => (
                    <Tag key={tag}>{tag}</Tag>
                  ))}
                </Descriptions.Item>
                <Descriptions.Item label="JSON">
                  <pre>{JSON.stringify(selectedClip3, null, 2)}</pre>
                </Descriptions.Item>
              </Descriptions>
            </div>
          )}
        </TabPane>
      </Tabs>
    </Row>
  </>
  );
};

export default VideoTriTabs;
