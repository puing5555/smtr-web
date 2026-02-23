import InfluencerDetailClient from './InfluencerDetailClient';

export async function generateStaticParams(): Promise<{ id: string }[]> {
  // 주요 인플루언서 ID들을 미리 정적으로 생성
  return [
    { id: 'corinpapa1106' },
    { id: '1' },
    { id: '2' },
    { id: '3' },
    { id: '4' }
  ];
}

export default async function InfluencerDetailPage({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params;
  
  return <InfluencerDetailClient id={id} />;
}