import React, { useState } from 'react';
import { Tabs, Descriptions, Tag, Row, Col } from 'antd';
import ReactPlayer from 'react-player';
import VideoClipList from './VideoClipList';

const { TabPane } = Tabs;

const VideoTabs = ({ videoClips, videoClips2 }) => {
  const [selectedClip1, setSelectedClip1] = useState(null);
  const [selectedClip2, setSelectedClip2] = useState(null);

  const handleClipClick1 = (clip) => {
    setSelectedClip1(clip);
  };

  const handleClipClick2 = (clip) => {
    setSelectedClip2(clip);
  };

  return (
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
                    <div style={{ maxHeight: '200px', overflow: 'auto' }}>
                      <pre>{JSON.stringify(selectedClip1, null, 2)}</pre>
                    </div>div>
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
                    <div style={{ maxHeight: '200px', overflow: 'auto' }}>
                      <pre>{JSON.stringify(selectedClip2, null, 2)}</pre>
                    </div>div>
                  </Descriptions.Item>
                </Descriptions>
              </div>
            )}
          </TabPane>
        </Tabs>
      </Col>
    </Row>
  );
};

export default VideoTabs;
