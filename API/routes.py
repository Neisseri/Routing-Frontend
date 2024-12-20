# Import the built-in libraries
import os
from datetime import datetime, timedelta

# Import external libraries
import numpy as np
import pandas as pd
import pickle
from flask import Blueprint, request, jsonify
import json

# Import customized libraries
from src.utils.helpers import DIR_DATA_BGP
from src.utils.downloader import BGPDataDownloader
from src.utils.geolocator import Geolocator
from src.analyze.topology_analysis import ASTopologyAnalyzer
from src.analyze.prefix_stats import PrefixStatisticsAnalyzer
from src.analyze.build_topology import ASTopologyBuilder

my_routes = Blueprint('my_routes', __name__)

topology_analyzer = ASTopologyAnalyzer()
prefix_analyzer = PrefixStatisticsAnalyzer()
topology_builder = ASTopologyBuilder()
downloader = BGPDataDownloader()
geolocator = Geolocator()

# ===================== 1. AS拓扑结构接口 =====================

@my_routes.route('/topology/country', methods=['GET'])
def get_country_topology():
    """获取国家级别的AS拓扑结构
    请求参数：
        - date: 可选，日期，格式YYYY-MM-DD，默认最新数据
    
    返回数据：
        {
            'nodes': [
                {
                    'country_code': str,
                    'country_name': str,
                    'lat': float,
                    'lon': float,
                    'as_count': int,
                    'total_announced': int,
                    'total_valid': int,
                    'avg_validity_ratio': float,
                    'asns': [
                        {
                            'asn': int,
                            'as_name': str
                        }
                    ]
                }
            ],
            'links': [
                {
                    'source': str(country_code),
                    'target': str(country_code),
                    'weight': int
                }
            ]
        }
    """
    try:
        date = request.args.get('date')
        if date:
            date = datetime.strptime(date, '%Y-%m-%d')
        else:
            date = datetime(2024, 12, 1)
        topology = topology_analyzer.get_country_topology(date)
        return jsonify(topology)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@my_routes.route('/topology/as/<int:asn>', methods=['GET'])
def get_as_stats(asn):
    """获取指定AS的统计数据
    返回数据：
        [
            {
                'date': str,
                'announced_prefixes': int,
                'valid_announcements': int,
                'validity_ratio': float
            }
        ]
    """
    try:
        stats = prefix_analyzer.get_stats_by_as(asn)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===================== 2. BGP更新查询接口 =====================

@my_routes.route('/updates/trend', methods=['GET'])
def get_prefix_trend():
    """获取全网BGP前缀变化趋势
    返回数据：
        [
            {
                'date': str,
                'announcements': int,
                'valid_announcements': int,
                'withdrawals': int,
                'validity_ratio': float,
                'net_change': int
            }
        ]
    """
    try:
        trend = prefix_analyzer.get_stats_by_date()
        return jsonify(trend)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@my_routes.route('/updates/search', methods=['GET'])
def search_updates():
    """搜索具体的BGP更新信息(分页)
    请求参数：
        - date: 可选，日期，格式YYYY-MM-DD，不指定则获取最近一天的数据
        - prefix: 可选，IP前缀
        - asn: 可选，AS号
        - page: 可选，页码，默认1
        - per_page: 可选，每页数量，默认50
    
    返回数据：
        {
            'total': int,       # 总记录数
            'total_pages': int, # 总页数
            'current_page': int,# 当前页码
            'data': [          # 当前页数据
                {
                    'timestamp': str,
                    'collector': str,
                    'type': int,  # 1=公告, 2=撤回
                    'prefix': str,
                    'origin_as': int,
                    'as_path': list[int],
                    'next_hop': str,
                    'valid': bool
                }
            ]
        }
    """
    try:
        # 获取参数
        date = request.args.get('date')
        prefix = request.args.get('prefix')
        asn = request.args.get('asn')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # 转换日期格式
        if date:
            date = datetime.strptime(date, '%Y-%m-%d')
        else:
            date = datetime(2024, 12, 1)
        if asn:
            asn = int(asn)
            
        # 获取分页数据
        updates = prefix_analyzer.get_updates_by_filter(
            date=date,
            prefix=prefix,
            asn=asn,
            page=page,
            per_page=per_page
        )
        return jsonify(updates)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===================== 3. 数据下载接口 =====================

@my_routes.route('/download/data', methods=['GET'])
def download_data():
    """下载指定日期的数据"""
    try:
        date = request.args.get('date')
        data_type = request.args.get('type')
        
        if not date or not data_type:
            return jsonify({'error': '缺少必需参数'}), 400
            
        date = datetime.strptime(date, '%Y-%m-%d')
        
        if data_type == 'updates':
            downloader.download_update_data(date, date + timedelta(days=1))
            prefix_analyzer.analyze_prefix_stats(date, date + timedelta(days=1))
        elif data_type == 'rib':
            downloader.download_rib_data(date, date + timedelta(days=1))
            topology_builder.build_topology_for_period(date, date + timedelta(days=1))
            geolocator.remove_missing_geo_links()
        else:
            return jsonify({'error': '无效的数据类型'}), 400

        return jsonify({'message': '下载完成'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# TODO: You need to implement extra functions for AS Topology or Real-Time BGP data feed.
# You should add more routes here!